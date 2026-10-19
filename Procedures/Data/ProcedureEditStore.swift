import Foundation

/// A section of a procedure that a clinician can rewrite in the app.
enum EditableSection: String, Codable, CaseIterable, Identifiable {
    case shiftMode, indications, contraindications, anatomy, equipment
    case positioning, steps, ultrasound, confirmation, troubleshooting
    case complications, aftercare, documentation, seniorPearls, references

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .shiftMode: return "Shift Mode"
        case .indications: return "Indications"
        case .contraindications: return "Contraindications / Cautions"
        case .anatomy: return "Anatomy / Landmarks"
        case .equipment: return "Equipment"
        case .positioning: return "Positioning"
        case .steps: return "Steps"
        case .ultrasound: return "Ultrasound Guidance"
        case .confirmation: return "Confirmation"
        case .troubleshooting: return "Troubleshooting"
        case .complications: return "Complications"
        case .aftercare: return "Aftercare"
        case .documentation: return "Documentation"
        case .seniorPearls: return "Senior Pearls"
        case .references: return "References"
        }
    }

    /// True for the sections that feed the review fingerprint, so the editor
    /// can warn that a change here is clinically material.
    ///
    /// Derived from `Procedure.materialSectionNames` rather than restated, so
    /// the editor's warning cannot drift out of step with what is actually
    /// hashed — they were separately maintained lists of the same three
    /// sections, and both were missing shiftMode.
    var isClinicallyMaterial: Bool {
        Procedure.materialSectionNames.contains(rawValue)
    }

    func lines(in sections: ProcedureSections) -> [String] {
        switch self {
        case .shiftMode: return sections.shiftMode
        case .indications: return sections.indications
        case .contraindications: return sections.contraindications
        case .anatomy: return sections.anatomy
        case .equipment: return sections.equipment
        case .positioning: return sections.positioning
        case .steps: return sections.steps
        case .ultrasound: return sections.ultrasound
        case .confirmation: return sections.confirmation
        case .troubleshooting: return sections.troubleshooting
        case .complications: return sections.complications
        case .aftercare: return sections.aftercare
        case .documentation: return sections.documentation
        case .seniorPearls: return sections.seniorPearls
        case .references: return sections.references
        }
    }

    func apply(_ lines: [String], to sections: inout ProcedureSections) {
        switch self {
        case .shiftMode: sections.shiftMode = lines
        case .indications: sections.indications = lines
        case .contraindications: sections.contraindications = lines
        case .anatomy: sections.anatomy = lines
        case .equipment: sections.equipment = lines
        case .positioning: sections.positioning = lines
        case .steps: sections.steps = lines
        case .ultrasound: sections.ultrasound = lines
        case .confirmation: sections.confirmation = lines
        case .troubleshooting: sections.troubleshooting = lines
        case .complications: sections.complications = lines
        case .aftercare: sections.aftercare = lines
        case .documentation: sections.documentation = lines
        case .seniorPearls: sections.seniorPearls = lines
        case .references: sections.references = lines
        }
    }
}

/// Which kind of card a card edit belongs to.
enum CardKind: String, Codable {
    case rescue, kit
}

/// A list on a rescue card or kit that a clinician can rewrite in the app.
/// Mirrors `CARD_FIELDS` in scripts/apply_local_edits.py.
enum CardField: String, Codable, CaseIterable, Identifiable {
    // Rescue cards
    case trigger, immediateMoves, avoid, reassess
    // Kits
    case inKit, outsideKit, commonlyForgotten, patientSetup, sterileSetup, backupEquipment

    var id: String { rawValue }

    static func fields(for kind: CardKind) -> [CardField] {
        switch kind {
        case .rescue: return [.immediateMoves, .trigger, .avoid, .reassess]
        case .kit: return [.inKit, .outsideKit, .commonlyForgotten, .patientSetup, .sterileSetup, .backupEquipment]
        }
    }

    var displayName: String {
        switch self {
        case .trigger: return "Recognize"
        case .immediateMoves: return "Immediate Moves"
        case .avoid: return "Avoid"
        case .reassess: return "Reassess"
        case .inKit: return "In the Kit"
        case .outsideKit: return "Outside the Kit"
        case .commonlyForgotten: return "Commonly Forgotten"
        case .patientSetup: return "Patient Setup"
        case .sterileSetup: return "Sterile Setup"
        case .backupEquipment: return "Backup Equipment"
        }
    }

    /// Every editable field except backup equipment feeds the card's review
    /// fingerprint, so a change there is clinically material.
    var isClinicallyMaterial: Bool { self != .backupEquipment }

    func lines(in card: ComplicationRescueCard) -> [String] {
        switch self {
        case .trigger: return card.trigger
        case .immediateMoves: return card.immediateMoves
        case .avoid: return card.avoid
        case .reassess: return card.reassess
        default: return []
        }
    }

    func apply(_ lines: [String], to card: inout ComplicationRescueCard) {
        switch self {
        case .trigger: card.trigger = lines
        case .immediateMoves: card.immediateMoves = lines
        case .avoid: card.avoid = lines
        case .reassess: card.reassess = lines
        default: break
        }
    }

    func lines(in kit: Kit) -> [String] {
        switch self {
        case .inKit: return kit.inKit
        case .outsideKit: return kit.outsideKit
        case .commonlyForgotten: return kit.commonlyForgotten
        case .patientSetup: return kit.patientSetup
        case .sterileSetup: return kit.sterileSetup
        case .backupEquipment: return kit.backupEquipment
        default: return []
        }
    }

    func apply(_ lines: [String], to kit: inout Kit) {
        switch self {
        case .inKit: kit.inKit = lines
        case .outsideKit: kit.outsideKit = lines
        case .commonlyForgotten: kit.commonlyForgotten = lines
        case .patientSetup: kit.patientSetup = lines
        case .sterileSetup: kit.sterileSetup = lines
        case .backupEquipment: kit.backupEquipment = lines
        default: break
        }
    }
}

/// One rescue card's or kit's locally authored overrides.
struct CardFieldEdits: Codable, Hashable {
    /// `CardField.rawValue` -> replacement lines. Only edited fields appear.
    var fields: [String: [String]] = [:]
    var editedAt: String = ""

    var isEmpty: Bool { fields.isEmpty }
}

/// One procedure's locally authored overrides.
struct ProcedureSectionEdits: Codable, Hashable {
    /// `EditableSection.rawValue` -> replacement lines. Only edited sections
    /// appear; everything else falls through to bundled content.
    var sections: [String: [String]] = [:]
    var editedAt: String = ""
    /// Bundled clinically material text when this local correction started.
    /// This lets recovery import warn when a saved correction would conceal a
    /// newer shipped procedure after an app update.
    var baseMaterialFingerprint: String?

    var isEmpty: Bool { sections.isEmpty }
}

/// Locally authored corrections to bundled clinical content.
///
/// An iOS app bundle is read-only, so `procedures.json` cannot be rewritten on
/// device. Instead each edited section is stored as an override in Documents
/// and merged over the bundled content when the repository loads. Bundled
/// content is never mutated — every section can be reverted to exactly what
/// shipped — and the overrides can be exported so corrections made at the
/// bedside can reach the repo instead of dying on one phone.
@MainActor
final class ProcedureEditStore: ObservableObject {
    @Published private(set) var editsByProcedureID: [String: ProcedureSectionEdits] = [:]
    @Published private(set) var hasUnreadableEdits = false
    /// Local corrections to rescue cards and kits, keyed by `cardKey(_:_:)`
    /// ("rescue:<id>" or "kit:<id>"). Stored in their own file so a damaged
    /// procedure store can never take card edits with it, or the reverse.
    @Published private(set) var cardEdits: [String: CardFieldEdits] = [:]

    private let fileURL: URL?
    private let cardFileURL: URL?
    /// Shipped card text, captured before any override is applied. Same
    /// reason as `bundledSections`: the repository publishes merged cards.
    private var bundledRescueCards: [String: ComplicationRescueCard] = [:]
    private var bundledKits: [String: Kit] = [:]

    /// Bundled section text, captured before any override is applied.
    ///
    /// The repository publishes *merged* procedures, so a `Procedure` handed to
    /// this store by a view already contains the clinician's edits. Comparing
    /// against that copy made "revert to bundled" restore the edit it was
    /// supposed to discard. The baseline is recorded here at load time instead,
    /// and it is deliberately not `@Published`: it is written during
    /// `applyEdits(to:)`, which runs inside a content load.
    private var bundledSections: [String: ProcedureSections] = [:]

    init(directory: URL? = nil) {
        let base = directory ?? FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
        fileURL = base?.appendingPathComponent("procedure_edits.json")
        cardFileURL = base?.appendingPathComponent("card_edits.json")
        load()
        loadCardEdits()
    }

    // MARK: - Reading

    func hasEdits(for procedureID: String) -> Bool {
        !(editsByProcedureID[procedureID]?.isEmpty ?? true)
    }

    var editedProcedureCount: Int {
        editsByProcedureID.values.filter { !$0.isEmpty }.count
    }

    func isEdited(_ section: EditableSection, procedureID: String) -> Bool {
        editsByProcedureID[procedureID]?.sections[section.rawValue] != nil
    }

    func editedSections(for procedureID: String) -> [EditableSection] {
        guard let edits = editsByProcedureID[procedureID] else { return [] }
        return EditableSection.allCases.filter { edits.sections[$0.rawValue] != nil }
    }

    /// Current text for a section: the local override when one exists,
    /// otherwise the bundled content.
    func lines(_ section: EditableSection, in procedure: Procedure) -> [String] {
        editsByProcedureID[procedure.id]?.sections[section.rawValue]
            ?? bundledLines(section, in: procedure)
    }

    /// The text that shipped, ignoring any override.
    ///
    /// Falls back to the passed procedure only when no baseline was recorded —
    /// a procedure the repository never loaded, which by definition has no
    /// override to strip.
    func bundledLines(_ section: EditableSection, in procedure: Procedure) -> [String] {
        section.lines(in: bundledSections[procedure.id] ?? procedure.sections)
    }

    // MARK: - Writing

    /// Stores an override. Blank lines are dropped, so an "empty" edit is a
    /// deliberate empty section rather than a list of whitespace.
    func setLines(_ lines: [String], for section: EditableSection, in procedure: Procedure) {
        let cleaned = lines
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }

        var edits = editsByProcedureID[procedure.id] ?? ProcedureSectionEdits()
        if edits.sections.isEmpty {
            var bundled = procedure
            bundled.sections = bundledSections[procedure.id] ?? procedure.sections
            edits.baseMaterialFingerprint = bundled.materialFingerprint
        }
        if cleaned == bundledLines(section, in: procedure) {
            // Identical to what shipped: store nothing rather than a no-op
            // override that would mark the procedure as edited forever.
            edits.sections.removeValue(forKey: section.rawValue)
        } else {
            edits.sections[section.rawValue] = cleaned
        }
        edits.editedAt = ContentFreshness.todayString()
        commit(edits, for: procedure.id)
    }

    func resetSection(_ section: EditableSection, in procedure: Procedure) {
        guard var edits = editsByProcedureID[procedure.id] else { return }
        edits.sections.removeValue(forKey: section.rawValue)
        commit(edits, for: procedure.id)
    }

    func resetAllEdits(for procedure: Procedure) {
        editsByProcedureID.removeValue(forKey: procedure.id)
        save()
    }

    func resetEverything() {
        editsByProcedureID = [:]
        save()
        cardEdits = [:]
        saveCardEdits()
    }

    private func commit(_ edits: ProcedureSectionEdits, for procedureID: String) {
        if edits.isEmpty {
            editsByProcedureID.removeValue(forKey: procedureID)
        } else {
            editsByProcedureID[procedureID] = edits
        }
        save()
    }

    // MARK: - Merging

    /// Overlays local edits onto bundled procedures. Unknown procedure IDs and
    /// unknown section keys are ignored, so stale overrides left by removed
    /// content can never corrupt what is displayed.
    func applyEdits(to procedures: [Procedure]) -> [Procedure] {
        // Capture what shipped before overlaying anything. This is the only
        // point in the app that sees unmerged content.
        for procedure in procedures {
            bundledSections[procedure.id] = procedure.sections
        }
        guard !editsByProcedureID.isEmpty else { return procedures }
        return procedures.map { procedure in
            guard let edits = editsByProcedureID[procedure.id], !edits.isEmpty else { return procedure }
            var updated = procedure
            var sections = procedure.sections
            for (key, lines) in edits.sections {
                guard let section = EditableSection(rawValue: key) else { continue }
                section.apply(lines, to: &sections)
            }
            updated.sections = sections
            return updated
        }
    }

    /// Drops overrides the bundle has caught up with.
    ///
    /// An override exists to keep a correction alive until it reaches the repo.
    /// Nothing ever retired one, so a correction merged upstream and shipped in
    /// a later build stayed here forever as a duplicate of the bundled text —
    /// still marking the procedure edited, still riding in every export. Twelve
    /// procedures were exported for merge when four of them had already landed
    /// builds ago, and the round-trip has no way to tell the difference: the
    /// same corrections get re-sent, re-read, and re-applied as no-ops for as
    /// long as the app is used.
    ///
    /// The bundle is the acknowledgement. A shipped build that already contains
    /// the correction is proof it was accepted, so no receipt, watermark, or
    /// manual bookkeeping is needed to know what has landed — and none of those
    /// could be trusted anyway, since only the bundle knows what the repo took.
    ///
    /// Retires only sections whose text is character-identical to what shipped,
    /// so nothing a clinician wrote is discarded and a section the repo has not
    /// caught up with is left alone. Reverting the retired section afterwards
    /// yields the same text either way, which is what makes this lossless.
    ///
    /// Only safe on a complete content load: a partial one leaves
    /// `bundledSections` empty or stale, and comparing against that would
    /// retire an override against text that never shipped.
    func retireLandedEdits() {
        guard !editsByProcedureID.isEmpty else { return }
        var didRetire = false
        for (procedureID, edits) in editsByProcedureID {
            guard let bundled = bundledSections[procedureID] else { continue }
            var remaining = edits
            for (key, lines) in edits.sections {
                guard let section = EditableSection(rawValue: key) else { continue }
                if section.lines(in: bundled) == lines {
                    remaining.sections.removeValue(forKey: key)
                }
            }
            guard remaining.sections.count != edits.sections.count else { continue }
            didRetire = true
            if remaining.isEmpty {
                editsByProcedureID.removeValue(forKey: procedureID)
            } else {
                editsByProcedureID[procedureID] = remaining
            }
        }
        if didRetire { save() }
    }

    /// Drops overrides for procedures that no longer exist. Only called when
    /// the bundled load was complete, so a transient failure never deletes a
    /// clinician's corrections.
    func pruneMissingProcedures(validProcedureIDs: Set<String>) {
        let original = Set(editsByProcedureID.keys)
        editsByProcedureID = editsByProcedureID.filter { validProcedureIDs.contains($0.key) }
        if Set(editsByProcedureID.keys) != original { save() }
    }

    /// The original bundled fingerprint for a visible procedure. The
    /// repository normally hands views merged procedures, so this deliberately
    /// reaches back to the captured pre-edit baseline.
    func bundledMaterialFingerprint(for procedureID: String, in procedures: [Procedure]) -> String? {
        guard var procedure = procedures.first(where: { $0.id == procedureID }) else { return nil }
        procedure.sections = bundledSections[procedureID] ?? procedure.sections
        return procedure.materialFingerprint
    }

    func restoreRecoveryEdits(_ restored: [String: ProcedureSectionEdits], replacingConflicts: Bool) {
        if replacingConflicts {
            for (procedureID, restoredEdit) in restored {
                editsByProcedureID[procedureID] = restoredEdit
            }
        } else {
            for (procedureID, restoredEdit) in restored where editsByProcedureID[procedureID] == nil {
                editsByProcedureID[procedureID] = restoredEdit
            }
        }
        save()
    }

    /// The unreadable sidecar remains on disk for forensic recovery, but an
    /// explicitly completed recovery makes the new primary store trustworthy
    /// again and allows automatic snapshots to resume.
    func markRecoveryRestored() {
        hasUnreadableEdits = false
    }

    // MARK: - Rescue card and kit edits

    static func cardKey(_ kind: CardKind, _ id: String) -> String {
        "\(kind.rawValue):\(id)"
    }

    var editedCardCount: Int {
        cardEdits.values.filter { !$0.isEmpty }.count
    }

    /// Procedures plus cards with local edits: what an export would carry.
    var editedItemCount: Int {
        editedProcedureCount + editedCardCount
    }

    func hasCardEdits(_ kind: CardKind, id: String) -> Bool {
        !(cardEdits[Self.cardKey(kind, id)]?.isEmpty ?? true)
    }

    func isCardFieldEdited(_ field: CardField, kind: CardKind, id: String) -> Bool {
        cardEdits[Self.cardKey(kind, id)]?.fields[field.rawValue] != nil
    }

    /// The text that shipped, ignoring any override.
    func bundledCardLines(_ field: CardField, kind: CardKind, id: String) -> [String] {
        switch kind {
        case .rescue: return bundledRescueCards[id].map { field.lines(in: $0) } ?? []
        case .kit: return bundledKits[id].map { field.lines(in: $0) } ?? []
        }
    }

    /// Current text: the local override when one exists, otherwise what shipped.
    func cardLines(_ field: CardField, kind: CardKind, id: String) -> [String] {
        cardEdits[Self.cardKey(kind, id)]?.fields[field.rawValue]
            ?? bundledCardLines(field, kind: kind, id: id)
    }

    func setCardLines(_ lines: [String], field: CardField, kind: CardKind, id: String) {
        let cleaned = lines
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        let key = Self.cardKey(kind, id)
        var edits = cardEdits[key] ?? CardFieldEdits()
        if cleaned == bundledCardLines(field, kind: kind, id: id) {
            edits.fields.removeValue(forKey: field.rawValue)
        } else {
            edits.fields[field.rawValue] = cleaned
        }
        edits.editedAt = ContentFreshness.todayString()
        commitCard(edits, forKey: key)
    }

    func resetCardField(_ field: CardField, kind: CardKind, id: String) {
        let key = Self.cardKey(kind, id)
        guard var edits = cardEdits[key] else { return }
        edits.fields.removeValue(forKey: field.rawValue)
        commitCard(edits, forKey: key)
    }

    func resetAllCardEdits(_ kind: CardKind, id: String) {
        cardEdits.removeValue(forKey: Self.cardKey(kind, id))
        saveCardEdits()
    }

    private func commitCard(_ edits: CardFieldEdits, forKey key: String) {
        if edits.isEmpty {
            cardEdits.removeValue(forKey: key)
        } else {
            cardEdits[key] = edits
        }
        saveCardEdits()
    }

    /// Overlays local edits onto bundled rescue cards. Records what shipped
    /// first. Unknown ids and field keys are ignored.
    func applyCardEdits(toRescueCards cards: [ComplicationRescueCard]) -> [ComplicationRescueCard] {
        for card in cards { bundledRescueCards[card.id] = card }
        guard !cardEdits.isEmpty else { return cards }
        return cards.map { card in
            guard let edits = cardEdits[Self.cardKey(.rescue, card.id)] else { return card }
            var updated = card
            for (key, lines) in edits.fields {
                CardField(rawValue: key)?.apply(lines, to: &updated)
            }
            return updated
        }
    }

    func applyCardEdits(toKits kits: [Kit]) -> [Kit] {
        for kit in kits { bundledKits[kit.id] = kit }
        guard !cardEdits.isEmpty else { return kits }
        return kits.map { kit in
            guard let edits = cardEdits[Self.cardKey(.kit, kit.id)] else { return kit }
            var updated = kit
            for (key, lines) in edits.fields {
                CardField(rawValue: key)?.apply(lines, to: &updated)
            }
            return updated
        }
    }

    /// Drops card overrides the bundle has caught up with, and overrides for
    /// cards that no longer ship. Same contract as `retireLandedEdits()`:
    /// call only after a complete load, and only identical text retires.
    func retireLandedCardEdits(validRescueIDs: Set<String>, validKitIDs: Set<String>) {
        guard !cardEdits.isEmpty else { return }
        var changed = false
        for (key, edits) in cardEdits {
            let parts = key.split(separator: ":", maxSplits: 1).map(String.init)
            guard parts.count == 2, let kind = CardKind(rawValue: parts[0]) else { continue }
            let id = parts[1]
            let exists = kind == .rescue ? validRescueIDs.contains(id) : validKitIDs.contains(id)
            if !exists {
                cardEdits.removeValue(forKey: key)
                changed = true
                continue
            }
            var remaining = edits
            for (fieldKey, lines) in edits.fields {
                guard let field = CardField(rawValue: fieldKey) else { continue }
                if bundledCardLines(field, kind: kind, id: id) == lines {
                    remaining.fields.removeValue(forKey: fieldKey)
                }
            }
            guard remaining.fields.count != edits.fields.count else { continue }
            changed = true
            if remaining.isEmpty {
                cardEdits.removeValue(forKey: key)
            } else {
                cardEdits[key] = remaining
            }
        }
        if changed { saveCardEdits() }
    }

    func restoreRecoveryCardEdits(_ restored: [String: CardFieldEdits], replacingConflicts: Bool) {
        for (key, edit) in restored where replacingConflicts || cardEdits[key] == nil {
            cardEdits[key] = edit
        }
        saveCardEdits()
    }

    private func loadCardEdits() {
        guard let cardFileURL, let data = try? Data(contentsOf: cardFileURL) else { return }
        if let decoded = try? JSONDecoder().decode([String: CardFieldEdits].self, from: data) {
            cardEdits = decoded
        } else {
            let unreadableURL = cardFileURL.appendingPathExtension("unreadable")
            if !FileManager.default.fileExists(atPath: unreadableURL.path) {
                try? data.write(to: unreadableURL, options: .atomic)
            }
            hasUnreadableEdits = true
        }
    }

    private func saveCardEdits() {
        guard let cardFileURL else { return }
        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            try encoder.encode(cardEdits).write(to: cardFileURL, options: .atomic)
        } catch {
            print("Failed to save card edits: \(error)")
        }
    }

    // MARK: - Export

    /// Serializes every local edit for transfer back into the repo. Paired with
    /// `scripts/apply_local_edits.py`, which merges this into procedures.json
    /// as a reviewable diff rather than a wholesale file replacement.
    func exportData() throws -> Data {
        let payload = ExportPayload(
            schema: Self.exportSchema,
            exportedAt: ContentFreshness.todayString(),
            edits: editsByProcedureID,
            cardEdits: cardEdits.isEmpty ? nil : cardEdits
        )
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return try encoder.encode(payload)
    }

    /// Writes the export to a temporary file for sharing. Returns nil when the
    /// write fails rather than trapping.
    func writeExportFile() -> URL? {
        do {
            let data = try exportData()
            let url = FileManager.default.temporaryDirectory
                .appendingPathComponent("procedure-edits-\(ContentFreshness.todayString()).json")
            try data.write(to: url, options: .atomic)
            return url
        } catch {
            print("Failed to write edit export: \(error)")
            return nil
        }
    }

    static let exportSchema = "procedures.local-edits.v1"

    private struct ExportPayload: Codable {
        let schema: String
        let exportedAt: String
        let edits: [String: ProcedureSectionEdits]
        /// Rescue card and kit edits, keyed "rescue:<id>" / "kit:<id>".
        /// Optional so an export with none matches the old format exactly.
        let cardEdits: [String: CardFieldEdits]?
    }

    // MARK: - Persistence

    private func load() {
        guard let fileURL, let data = try? Data(contentsOf: fileURL) else { return }
        if let decoded = try? JSONDecoder().decode([String: ProcedureSectionEdits].self, from: data) {
            editsByProcedureID = decoded
        } else {
            // Preserve the only copy before any later edit can replace it.
            let unreadableURL = fileURL.appendingPathExtension("unreadable")
            if !FileManager.default.fileExists(atPath: unreadableURL.path) {
                try? data.write(to: unreadableURL, options: .atomic)
            }
            hasUnreadableEdits = true
        }
    }

    private func save() {
        guard let fileURL else { return }
        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            try encoder.encode(editsByProcedureID).write(to: fileURL, options: .atomic)
        } catch {
            print("Failed to save procedure edits: \(error)")
        }
    }

}
