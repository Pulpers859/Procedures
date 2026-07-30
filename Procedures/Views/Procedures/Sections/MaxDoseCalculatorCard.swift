import SwiftUI

/// Weight-based local-anesthetic ceiling, computed rather than written down.
///
/// This replaces a card that printed a frozen worked example beside an
/// absolute maximum. On the digital block the two disagreed — "70 kg = 315 mg"
/// under "absolute max 300 mg" — because a sentence cannot recalculate itself
/// and the ceiling was added later. Everything here is derived from the same
/// three numbers the record declares, so the two cannot drift apart again.
///
/// Weight is deliberately not persisted. It belongs to a patient, not to the
/// app, and a weight left over from the last shift is a worse failure than
/// retyping two digits.
struct MaxDoseCalculatorCard: View {
    let dosing: ProcedureDosing

    @State private var weightText = ""
    @State private var selectedAgentID: String?
    @State private var selectedPercent: Double?

    private var weightKg: Double? {
        // Locale matters: a comma decimal separator is a real keyboard on a
        // real phone, and parsing it as nothing is safer than parsing "1,5"
        // as 15 — but silently dropping it is confusing, so accept both.
        let normalized = weightText
            .trimmingCharacters(in: .whitespaces)
            .replacingOccurrences(of: ",", with: ".")
        guard let value = Double(normalized), value > 0, value <= 500 else { return nil }
        return value
    }

    private var agent: ProcedureDosing.Agent? {
        dosing.agents.first { $0.id == selectedAgentID } ?? dosing.agents.first
    }

    private var percent: Double? {
        guard let agent else { return nil }
        if let selectedPercent, agent.concentrationsPercent.contains(selectedPercent) {
            return selectedPercent
        }
        return agent.concentrationsPercent.first
    }

    var body: some View {
        SectionCard(title: "Max Dose — Calculate Before You Draw Up", systemImage: "scalemass") {
            VStack(alignment: .leading, spacing: 16) {
                inputs
                if let agent, let percent, let weightKg {
                    result(agent: agent, percent: percent, weightKg: weightKg)
                } else {
                    Text("Enter a weight to calculate the maximum.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Divider()
                reference
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

    // MARK: - Inputs

    @ViewBuilder
    private var inputs: some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text("Weight")
                        .font(.subheadline.weight(.semibold))
                    Spacer()
                    TextField("0", text: $weightText)
                        .keyboardType(.decimalPad)
                        .multilineTextAlignment(.trailing)
                        .frame(maxWidth: 110)
                        .textFieldStyle(.roundedBorder)
                        .accessibilityLabel("Patient weight in kilograms")
                    Text("kg")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Text("Use lean body weight in obese patients.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            if dosing.agents.count > 1 {
                Picker("Agent", selection: Binding(
                    get: { agent?.id ?? "" },
                    set: { newValue in
                        selectedAgentID = newValue
                        // The strengths differ per drug, so a strength carried
                        // over from the previous pick would be a lie about
                        // what is in the vial.
                        selectedPercent = nil
                    }
                )) {
                    ForEach(dosing.agents) { option in
                        Text(option.displayName).tag(option.id)
                    }
                }
                .pickerStyle(.menu)
            }

            if let agent, agent.concentrationsPercent.count > 1 {
                Picker("Strength", selection: Binding(
                    get: { percent ?? agent.concentrationsPercent[0] },
                    set: { selectedPercent = $0 }
                )) {
                    ForEach(agent.concentrationsPercent, id: \.self) { option in
                        Text(Self.percentLabel(option)).tag(option)
                    }
                }
                .pickerStyle(.segmented)
            }
        }
    }

    // MARK: - Result

    @ViewBuilder
    private func result(agent: ProcedureDosing.Agent, percent: Double, weightKg: Double) -> some View {
        let milligrams = agent.maxMilligrams(forWeightKg: weightKg)
        let capped = agent.isCapped(atWeightKg: weightKg)
        let millilitres = milligrams / ProcedureDosing.Agent.mgPerML(percent: percent)

        VStack(alignment: .leading, spacing: 4) {
            Text("Maximum for \(Self.number(weightKg)) kg")
                .font(.subheadline)
                .foregroundStyle(.secondary)
            Text(Self.milligramLabel(milligrams) + (capped ? "*" : ""))
                .font(.title2.weight(.bold))
                .foregroundStyle(AppSemanticColor.warningText)
            Text("\(Self.millilitreLabel(millilitres)) of \(Self.percentLabel(percent)) \(agent.displayName.lowercased())")
                .font(.body.weight(.semibold))
                .fixedSize(horizontal: false, vertical: true)

            if capped, let absolute = agent.absoluteMaxMg {
                Text("* Held at the \(Self.milligramLabel(absolute)) absolute maximum. "
                     + "\(Self.number(agent.maxDoseMgPerKg)) mg/kg at this weight would be "
                     + "\(Self.milligramLabel(agent.maxDoseMgPerKg * weightKg)) — the ceiling does not scale further.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            if let note = agent.note {
                Text(note)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Text("Reduce by about 25% at the extremes of age or with severe comorbidity.")
                .font(.footnote)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .accessibilityElement(children: .combine)
    }

    // MARK: - Reference table

    @ViewBuilder
    private var reference: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Ceilings")
                .font(.subheadline.weight(.semibold))
            ForEach(dosing.agents) { option in
                VStack(alignment: .leading, spacing: 2) {
                    Text("\(option.displayName): \(Self.number(option.maxDoseMgPerKg)) mg/kg"
                         + (option.absoluteMaxMg.map { ", absolute max \(Self.milligramLabel($0))" }
                            ?? ", no absolute ceiling"))
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                    if let note = option.note {
                        Text(note)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
        }
    }

    // MARK: - Formatting

    /// Floors rather than rounds. A maximum rounded up is a maximum exceeded,
    /// and 0.05 mL of bupivacaine is not worth the precedent.
    static func millilitreLabel(_ value: Double) -> String {
        String(format: "%.1f mL", (value * 10).rounded(.down) / 10)
    }

    static func milligramLabel(_ value: Double) -> String {
        "\(number(value.rounded(.down))) mg"
    }

    static func percentLabel(_ value: Double) -> String {
        "\(number(value))%"
    }

    static func number(_ value: Double) -> String {
        value.truncatingRemainder(dividingBy: 1) == 0
            ? String(Int(value))
            : String(value)
    }
}
