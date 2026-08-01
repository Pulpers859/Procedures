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

    private let fileURL: URL?

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
        load()
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

    // MARK: - Export

    /// Serializes every local edit for transfer back into the repo. Paired with
    /// `scripts/apply_local_edits.py`, which merges this into procedures.json
    /// as a reviewable diff rather than a wholesale file replacement.
    func exportData() throws -> Data {
        let payload = ExportPayload(
            schema: Self.exportSchema,
            exportedAt: ContentFreshness.todayString(),
            edits: editsByProcedureID
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
