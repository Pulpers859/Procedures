import SwiftUI

struct ShiftModeProcedureContent: View {
    let procedure: Procedure

    // Troubleshooting ("If It Fails") lives only on the Rescue tab
    // (ComplicationContent). It used to render here too, byte-identical -
    // anyone checking both tabs for the same procedure read the same card
    // twice for no reason.
    var body: some View {
        VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
            CriticalWarningCard(title: "Before You Start", items: procedure.sections.shiftMode)

            if let dosing = procedure.dosing {
                MaxDoseCalculatorCard(dosing: dosing)
            }

            if let medicationDosing = procedure.medicationDosing {
                MedicationDosingCard(dosing: medicationDosing)
            }

            if !procedure.sections.seniorPearls.isEmpty {
                SectionCard(title: "Technique Notes", systemImage: "quote.bubble") {
                    BulletListView(items: procedure.sections.seniorPearls)
                }
            }
        }
    }
}

/// Systemic medication doses. Deliberately not the "Max Dose" card: these are
/// target doses, and a range is shown as a range so it cannot be read as a
/// ceiling.
struct MedicationDosingCard: View {
    let dosing: ProcedureMedicationDosing

    var body: some View {
        SectionCard(title: "Medication Doses", systemImage: "syringe") {
            VStack(alignment: .leading, spacing: 12) {
                Text(dosing.indication)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)

                Label {
                    Text(dosing.inductionRequirement)
                        .font(.subheadline.weight(.medium))
                        .fixedSize(horizontal: false, vertical: true)
                } icon: {
                    Image(systemName: "exclamationmark.triangle")
                        .foregroundStyle(AppSemanticColor.warningText)
                }

                ForEach(dosing.medications) { med in
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(med.medication): \(doseLine(for: med))")
                            .font(.body.weight(.semibold))
                            .fixedSize(horizontal: false, vertical: true)
                        Text(detailLine(for: med))
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                        if let caution = med.caution {
                            Text(caution)
                                .font(.subheadline)
                                .foregroundStyle(AppSemanticColor.warningText)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }

                if let guidance = dosing.selectionGuidance, !guidance.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Agent of choice")
                            .font(.subheadline.weight(.semibold))
                        BulletListView(items: guidance)
                    }
                }

                Text(dosing.sourceNote)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    /// A range reads "0.6-1.2 mg/kg (range)". The suffix is not decoration: it
    /// is what stops the upper bound being read as a maximum.
    private func doseLine(for med: ProcedureMedicationDosing.Medication) -> String {
        guard med.isRange, let high = med.doseHighPerKg else {
            return "\(trimmed(med.doseLowPerKg)) \(med.unit)"
        }
        return "\(trimmed(med.doseLowPerKg))-\(trimmed(high)) \(med.unit) (range)"
    }

    private func detailLine(for med: ProcedureMedicationDosing.Medication) -> String {
        [med.role, med.onset.map { "onset \($0)" }, med.durationNote]
            .compactMap { $0 }
            .joined(separator: " · ")
    }

    private func trimmed(_ value: Double) -> String {
        value.truncatingRemainder(dividingBy: 1) == 0
            ? String(Int(value))
            : String(value)
    }
}
