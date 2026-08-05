import SwiftUI

/// Standing monitoring requirement for major regional blocks. Previously
/// copy-pasted as an `equipment` checklist line into 14 procedures - a change
/// to the standard meant editing 14 separate entries, with no way to catch
/// one left behind. Centralized here instead; `Procedure.majorBlockMonitoring`
/// flags which procedures render it.
enum MajorBlockMonitoring {
    static let requirement = "IV access, blood pressure, ECG, and pulse oximetry in place before the needle goes in. Major block."
}

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

                    if procedure.sections.equipment.isEmpty && !procedure.requiresMajorBlockMonitoring {
                        // Setup is a primary tab, not an overflow one - an
                        // empty ForEach here left the card showing a caption
                        // and a Reset button over nothing, which reads as
                        // broken rather than as "nothing to check."
                        Text("No equipment listed for this procedure.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(procedure.sections.equipment, id: \.self) { item in
                            ChecklistRow(
                                text: item,
                                isChecked: userData.isEquipmentChecked(item, for: procedure),
                                action: { userData.toggleEquipment(item, for: procedure) }
                            )
                        }
                        if procedure.requiresMajorBlockMonitoring {
                            ChecklistRow(
                                text: MajorBlockMonitoring.requirement,
                                isChecked: userData.isEquipmentChecked(MajorBlockMonitoring.requirement, for: procedure),
                                action: { userData.toggleEquipment(MajorBlockMonitoring.requirement, for: procedure) }
                            )
                        }
                    }
                }
            }
        }
        .alert("Reset all equipment items?", isPresented: $showingResetConfirmation) {
            Button("Reset Checklist", role: .destructive) {
                userData.resetEquipment(for: procedure)
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This clears the current equipment checks for this procedure.")
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
