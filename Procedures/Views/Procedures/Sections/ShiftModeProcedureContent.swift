import SwiftUI

struct ShiftModeProcedureContent: View {
    let procedure: Procedure

    var body: some View {
        VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
            CriticalWarningCard(title: "Before You Start", items: procedure.sections.shiftMode)

            if let dosing = procedure.dosing {
                DosingLimitsCard(dosing: dosing)
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
                        .foregroundStyle(.orange)
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
