import Foundation

struct ComplicationRescueCard: Identifiable, Hashable {
    enum Acuity: String, Hashable {
        case crash = "Crash"
        case urgent = "Urgent"
        case watch = "Watch"
    }

    let id: String
    let title: String
    let acuity: Acuity
    let relatedProcedureIDs: [String]
    let trigger: [String]
    let immediateMoves: [String]
    let reassess: [String]
    let avoid: [String]
    let tags: [String]

    func matches(_ query: String) -> Bool {
        let normalized = query.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalized.isEmpty else { return true }
        let haystack = ([title, acuity.rawValue] + relatedProcedureIDs + trigger + immediateMoves + reassess + avoid + tags)
            .joined(separator: " ")
            .lowercased()
        return normalized.split(separator: " ").allSatisfy { haystack.contains($0) }
    }
}

enum ComplicationRescueCardStore {
    static let cards: [ComplicationRescueCard] = [
        .init(
            id: "post_intubation_hypotension",
            title: "Post-intubation hypotension",
            acuity: .crash,
            relatedProcedureIDs: ["endotracheal_intubation"],
            trigger: ["New hypotension after RSI, tube placement, or positive-pressure ventilation."],
            immediateMoves: [
                "Confirm pulse, blood pressure, waveform, oxygenation, and tube depth.",
                "Disconnect briefly if severe auto-PEEP/dynamic hyperinflation is plausible.",
                "Reduce excessive PEEP or tidal volume while maintaining oxygenation.",
                "Give push-dose vasopressor if crashing and start norepinephrine early.",
                "Consider tension pneumothorax, mainstem intubation, hemorrhage, sepsis, or peri-intubation arrest physiology."
            ],
            reassess: ["ETCO2 waveform", "Lung sliding/bilateral breath sounds", "Vent pressures", "Repeat BP every 1–2 minutes until stable"],
            avoid: ["Do not assume the tube is the only problem.", "Do not forget analgesia/sedation after paralysis wears off."],
            tags: ["RSI", "ETT", "pressor", "shock", "hypotension", "ventilator"]
        ),
        .init(
            id: "failed_airway",
            title: "Failed airway / cannot intubate",
            acuity: .crash,
            relatedProcedureIDs: ["endotracheal_intubation", "cricothyrotomy"],
            trigger: ["Failed attempts, falling oxygen saturation, poor view, inability to ventilate, or airway contamination."],
            immediateMoves: [
                "Call failed-airway plan out loud and assign roles.",
                "Reoxygenate with two-hand BVM, oral/nasal airway, PEEP valve, and suction.",
                "Change something before the next attempt: operator, blade, position, device, bougie, or approach.",
                "Place supraglottic airway if BVM or intubation is failing and time allows.",
                "Move to front-of-neck access if cannot oxygenate."
            ],
            reassess: ["SpO2 trend", "Chest rise", "ETCO2 if ventilating", "Number of attempts", "Time since paralysis"],
            avoid: ["Do not repeat the same failed attempt.", "Do not burn the last 30 seconds debating while oxygenation is failing."],
            tags: ["airway", "cric", "surgical airway", "hypoxia", "bougie", "SGA"]
        ),
        .init(
            id: "arterial_puncture_cvc",
            title: "Arterial puncture during central line",
            acuity: .urgent,
            relatedProcedureIDs: ["central_venous_catheter", "cordis_introducer", "vas_cath"],
            trigger: ["Bright pulsatile blood, arterial waveform, high-pressure tubing, or ultrasound concern during access."],
            immediateMoves: [
                "Stop. Keep wire/catheter controlled; do not dilate if position is uncertain.",
                "Confirm with ultrasound, pressure transduction, blood gas, or waveform if stable enough.",
                "If only small finder/needle puncture, remove and hold firm pressure.",
                "If dilator or large catheter entered artery, leave it in place and call vascular/surgery immediately.",
                "Document event, site, exam, and consultation."
            ],
            reassess: ["Distal pulses", "Expanding hematoma", "Airway compression risk for neck sites", "Neurovascular status"],
            avoid: ["Never pull a large-bore arterial catheter and 'just hold pressure' without the right backup."],
            tags: ["CVC", "central line", "IJ", "femoral", "artery", "dilator"]
        ),
        .init(
            id: "lost_wire",
            title: "Lost guidewire / wire control problem",
            acuity: .crash,
            relatedProcedureIDs: ["central_venous_catheter", "cordis_introducer", "vas_cath"],
            trigger: ["Wire no longer visible or control of the proximal wire is lost."],
            immediateMoves: [
                "Stop the procedure immediately.",
                "Do not advance catheter or dilator blindly.",
                "Obtain imaging to localize the wire if not immediately retrievable.",
                "Call IR/vascular based on local resources.",
                "File safety event and document honestly."
            ],
            reassess: ["Patient rhythm", "Chest symptoms", "Wire location", "Need for retrieval"],
            avoid: ["Do not pretend it did not happen. This is a patient-safety emergency."],
            tags: ["central line", "wire", "guidewire", "CVC", "seldinger"]
        ),
        .init(
            id: "failed_transvenous_capture",
            title: "Failed transvenous pacer capture",
            acuity: .crash,
            relatedProcedureIDs: ["transvenous_pacemaker"],
            trigger: ["Pacer spikes without electrical/mechanical capture, persistent bradycardia, or unstable hypotension."],
            immediateMoves: [
                "Confirm generator is on, rate appropriate, output high, and connections secure.",
                "Increase mA until capture, then set safety margin above threshold.",
                "Slowly advance/withdraw catheter while watching ECG and patient pulse/BP.",
                "Use ultrasound/fluoro/CXR if available to confirm course.",
                "Continue transcutaneous pacing/pressors while troubleshooting."
            ],
            reassess: ["Electrical capture", "Mechanical pulse", "Blood pressure", "Pain/sedation needs", "Catheter depth"],
            avoid: ["Do not accept electrical spikes as success without a pulse/BP response."],
            tags: ["pacer", "TVP", "bradycardia", "capture", "transcutaneous"]
        ),
        .init(
            id: "sedation_apnea",
            title: "Procedural sedation apnea",
            acuity: .crash,
            relatedProcedureIDs: ["procedural_sedation"],
            trigger: ["Hypoventilation, apnea, desaturation, loss of airway tone, or rising ETCO2 during sedation."],
            immediateMoves: [
                "Stop sedative dosing and call for airway help.",
                "Reposition airway, jaw thrust, suction, and add oral/nasal airway as needed.",
                "BVM with PEEP if ventilation inadequate.",
                "Consider reversal only when appropriate for agent/context; do not delay ventilation.",
                "Prepare for intubation if oxygenation or ventilation cannot be maintained."
            ],
            reassess: ["ETCO2 waveform", "Chest rise", "SpO2", "Hemodynamics", "Return of protective airway reflexes"],
            avoid: ["Do not stare at the pulse ox while the patient is not ventilating."],
            tags: ["sedation", "apnea", "hypoxia", "ETCO2", "BVM", "airway"]
        )
    ]
}
