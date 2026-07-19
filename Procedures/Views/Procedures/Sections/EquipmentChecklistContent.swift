import SwiftUI

struct EquipmentChecklistContent: View {
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    @State private var showingResetConfirmation = false

    private var requiresSessionDecision: Bool {
        userData.requiresEquipmentSessionDecision(for: procedure)
    }

    var body: some View {
        SectionCard(title: "Room + Equipment Checklist", systemImage: "checklist") {
            if requiresSessionDecision {
                sessionDecision
            } else {
                VStack(alignment: .leading, spacing: 12) {
                    ViewThatFits(in: .horizontal) {
                        HStack {
                            checklistCaption
                            Spacer()
                            resetButton
                        }
                        VStack(alignment: .leading, spacing: 4) {
                            checklistCaption
                            resetButton
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
        .confirmationDialog("Reset all equipment items?", isPresented: $showingResetConfirmation, titleVisibility: .visible) {
            Button("Reset Checklist", role: .destructive) {
                userData.resetEquipment(for: procedure)
            }
        }
    }

    private var checklistCaption: some View {
        Text("Confirm what is physically in the room.")
            .font(.footnote)
            .foregroundStyle(.secondary)
    }

    private var resetButton: some View {
        Button("Reset") {
            showingResetConfirmation = true
        }
        .font(.footnote.weight(.semibold))
        .frame(minHeight: AppLayout.controlMinHeight)
    }

    private var sessionDecision: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Saved checks may be from a prior patient or room. Choose before using this checklist.")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            ViewThatFits(in: .horizontal) {
                HStack(spacing: 10) { sessionButtons }
                VStack(spacing: 8) { sessionButtons }
            }
        }
    }

    @ViewBuilder
    private var sessionButtons: some View {
        Button("Resume Saved") {
            userData.resumeEquipmentSession(for: procedure)
        }
        .buttonStyle(.borderedProminent)
        .frame(minHeight: AppLayout.controlMinHeight)

        Button("Start New", role: .destructive) {
            userData.resetEquipment(for: procedure)
        }
        .buttonStyle(.bordered)
        .frame(minHeight: AppLayout.controlMinHeight)
    }
}
