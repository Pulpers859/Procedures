import SwiftUI

struct ShiftModeProcedureContent: View {
    let procedure: Procedure

    var body: some View {
        VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
            CriticalWarningCard(title: "Before You Start", items: procedure.sections.shiftMode)

            if let dosing = procedure.dosing {
                DosingLimitsCard(dosing: dosing)
            }

            if let medicationDosing = procedure.medicationDosing {
                MedicationDosingCard(dosing: medicationDosing)
            }

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

/// Max-dose safety block rendered from `ProcedureDosing` content data. The
/// dose lines use larger type than body copy on purpose: this is the one card
/// that must be legible from arm's length before the operator draws up.
struct DosingLimitsCard: View {
    let dosing: ProcedureDosing

    var body: some View {
        SectionCard(title: "Max Dose — Calculate Before You Draw Up", systemImage: "scalemass") {
            VStack(alignment: .leading, spacing: 12) {
                ForEach(dosing.agents) { agent in
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(agent.agent): \(maxLine(for: agent))")
                            .font(.body.weight(.semibold))
                            .fixedSize(horizontal: false, vertical: true)
                        Text(agent.concentrationNote)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                }

                Text(dosing.workedExample)
                    .font(.subheadline)
                    .fixedSize(horizontal: false, vertical: true)

                Label {
                    Text(dosing.cumulativeWarning)
                        .font(.subheadline.weight(.medium))
                        .fixedSize(horizontal: false, vertical: true)
                } icon: {
                    Image(systemName: "plus.forwardslash.minus")
                        .foregroundStyle(AppSemanticColor.warningText)
                }

                if !dosing.monitoring.isEmpty {
                    BulletListView(items: dosing.monitoring)
                }
            }
        }
    }

    private func maxLine(for agent: ProcedureDosing.Agent) -> String {
        let perKg = trimmed(agent.maxDoseMgPerKg)
        if let ceiling = agent.absoluteMaxMg {
            return "max \(perKg) mg/kg (absolute max \(trimmed(ceiling)) mg)"
        }
        return "max \(perKg) mg/kg"
    }

    private func trimmed(_ value: Double) -> String {
        value.truncatingRemainder(dividingBy: 1) == 0
            ? String(Int(value))
            : String(value)
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
