import SwiftUI

/// Section list for editing one procedure's text.
///
/// The point of the review workspace is to fix what you find. Before this
/// existed the only options were marking a row "Needs Edits" or typing a note
/// nothing ever read, so a correction spotted at the bedside had to be
/// transcribed into the repo by hand. Edits here are stored locally, overlay
/// the bundled content everywhere, and can be exported back to the repo.
struct ProcedureEditorView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var editStore: ProcedureEditStore
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure

    @State private var confirmResetAll = false

    var body: some View {
        List {
            Section {
                Text("Edits are stored on this device and replace the bundled text everywhere. Any section can be reverted.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Section("Sections") {
                ForEach(EditableSection.allCases) { section in
                    NavigationLink {
                        SectionEditorView(procedure: procedure, section: section)
                    } label: {
                        sectionRow(section)
                    }
                }
            }

            if editStore.hasEdits(for: procedure.id) {
                Section {
                    Button(role: .destructive) {
                        confirmResetAll = true
                    } label: {
                        Label("Revert All Sections", systemImage: "arrow.uturn.backward")
                            .frame(minHeight: AppLayout.controlMinHeight)
                    }
                } footer: {
                    Text("Restores every section of this procedure to the bundled text.")
                }
            }
        }
        .navigationTitle("Edit Content")
        .navigationBarTitleDisplayMode(.inline)
        .alert("Revert every section of \(procedure.title) to the bundled text?", isPresented: $confirmResetAll) {
            Button("Revert All", role: .destructive) {
                let previousFingerprint = currentProcedure?.materialFingerprint
                editStore.resetAllEdits(for: procedure)
                repository.reapplyEdits()
                rebaselineOwnReview(previousFingerprint: previousFingerprint)
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This removes the local content edits for this procedure.")
        }
    }

    private var currentProcedure: Procedure? {
        repository.procedures.first(where: { $0.id == procedure.id })
    }

    /// Reverting is still your own change, so it must not flag you to
    /// re-review your own work either.
    private func rebaselineOwnReview(previousFingerprint: String?) {
        guard let updated = currentProcedure else { return }
        userData.rebaselineReviewAfterLocalEdit(for: updated, previousFingerprint: previousFingerprint)
    }

    private func sectionRow(_ section: EditableSection) -> some View {
        let lines = editStore.lines(section, in: procedure)
        let isEdited = editStore.isEdited(section, procedureID: procedure.id)
        return HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 3) {
                Text(section.displayName)
                    .font(.subheadline.weight(.semibold))
                Text(lines.isEmpty ? "Empty" : "\(lines.count) line\(lines.count == 1 ? "" : "s")")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer(minLength: 8)
            if isEdited {
                Text("EDITED")
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(AppSemanticColor.warningText)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.14), in: Capsule())
            }
        }
        .padding(.vertical, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            "\(section.displayName), \(lines.count) lines\(isEdited ? ", edited" : "")"
        )
    }
}

/// Line-by-line editor for a single section.
struct SectionEditorView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var editStore: ProcedureEditStore
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    let section: EditableSection

    @State private var lines: [String] = []
    @State private var loaded = false
    @State private var confirmRevert = false
    @FocusState private var focusedLine: Int?

    var body: some View {
        List {
            if section.isClinicallyMaterial {
                Section {
                    Label(
                        "Clinically material content. The existing review stays as it is. Exporting will not promote the sign-off until the edit is applied to the bundled content.",
                        systemImage: "exclamationmark.triangle.fill"
                    )
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(AppSemanticColor.warningText)
                    .fixedSize(horizontal: false, vertical: true)
                }
            }

            Section {
                ForEach(Array(lines.enumerated()), id: \.offset) { index, _ in
                    TextField(
                        "Line \(index + 1)",
                        text: Binding(
                            get: { index < lines.count ? lines[index] : "" },
                            set: { if index < lines.count { lines[index] = $0 } }
                        ),
                        axis: .vertical
                    )
                    .focused($focusedLine, equals: index)
                    .font(.body)
                    .accessibilityLabel("\(section.displayName) line \(index + 1)")
                }
                .onDelete { offsets in
                    focusedLine = nil
                    lines.remove(atOffsets: offsets)
                    save()
                }
                .onMove { source, destination in
                    focusedLine = nil
                    lines.move(fromOffsets: source, toOffset: destination)
                    save()
                }

                Button {
                    lines.append("")
                    focusedLine = lines.count - 1
                } label: {
                    Label("Add Line", systemImage: "plus.circle.fill")
                        .frame(minHeight: AppLayout.controlMinHeight)
                }
            } header: {
                Text(section.displayName)
            } footer: {
                Text("Swipe a line to delete it. Blank lines are discarded on save.")
            }

            if editStore.isEdited(section, procedureID: procedure.id) {
                Section {
                    Button(role: .destructive) {
                        confirmRevert = true
                    } label: {
                        Label("Revert to Bundled Text", systemImage: "arrow.uturn.backward")
                            .frame(minHeight: AppLayout.controlMinHeight)
                    }
                }
            }
        }
        .navigationTitle(section.displayName)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) { EditButton() }
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()
                Button("Done") { focusedLine = nil }
            }
        }
        .onAppear {
            // Load once. Re-reading on every appear would discard in-progress
            // edits when the keyboard or a sheet causes a re-layout.
            guard !loaded else { return }
            lines = editStore.lines(section, in: procedure)
            loaded = true
        }
        .onDisappear { save() }
        .scrollDismissesKeyboard(.interactively)
        .alert("Revert \(section.displayName) to the bundled text?", isPresented: $confirmRevert) {
            Button("Revert", role: .destructive) {
                let previousFingerprint = currentProcedure?.materialFingerprint
                editStore.resetSection(section, in: procedure)
                repository.reapplyEdits()
                rebaselineOwnReview(previousFingerprint: previousFingerprint)
                // Read the baseline from the store, not from `procedure`: the
                // repository publishes merged content, so this copy still
                // carries the edit that was just discarded.
                lines = editStore.bundledLines(section, in: procedure)
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This removes the local edit for this section.")
        }
    }

    /// Normalized the same way `setLines` normalizes, so a trailing blank from
    /// "Add Line" does not read as a change.
    private var normalizedLines: [String] {
        lines.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
    }

    private func save() {
        // `onDisappear` fires whether or not anything was typed. Saving a
        // no-op used to re-decode and re-validate the whole library, rebuild
        // the search index, and reindex Spotlight — on the one screen where
        // the reader is typing.
        guard normalizedLines != editStore.lines(section, in: procedure) else { return }

        let previousFingerprint = currentProcedure?.materialFingerprint
        editStore.setLines(lines, for: section, in: procedure)
        repository.reapplyEdits()
        rebaselineOwnReview(previousFingerprint: previousFingerprint)
    }

    private var currentProcedure: Procedure? {
        repository.procedures.first(where: { $0.id == procedure.id })
    }

    /// Your own correction must not flag you to re-review your own work. Read
    /// the merged procedure back from the repository so the new baseline is the
    /// text that is actually being displayed.
    private func rebaselineOwnReview(previousFingerprint: String?) {
        guard let updated = currentProcedure else { return }
        userData.rebaselineReviewAfterLocalEdit(for: updated, previousFingerprint: previousFingerprint)
    }
}

/// Field list for editing one rescue card or kit. Same model as
/// `ProcedureEditorView`: edits are stored on this device, overlay the bundled
/// text everywhere, and leave the Review Center in the same export as
/// procedure edits.
struct CardEditorView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var editStore: ProcedureEditStore
    @EnvironmentObject private var userData: UserDataStore
    let kind: CardKind
    let id: String
    let title: String

    @State private var confirmResetAll = false

    var body: some View {
        List {
            Section {
                Text("Edits are stored on this device and replace the bundled text everywhere. Any list can be reverted.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Section("Lists") {
                ForEach(CardField.fields(for: kind)) { field in
                    NavigationLink {
                        CardFieldEditorView(kind: kind, id: id, field: field)
                    } label: {
                        fieldRow(field)
                    }
                }
            }

            if editStore.hasCardEdits(kind, id: id) {
                Section {
                    Button(role: .destructive) {
                        confirmResetAll = true
                    } label: {
                        Label("Revert All Lists", systemImage: "arrow.uturn.backward")
                            .frame(minHeight: AppLayout.controlMinHeight)
                    }
                } footer: {
                    Text("Restores every list on this card to the bundled text.")
                }
            }
        }
        .navigationTitle("Edit Content")
        .navigationBarTitleDisplayMode(.inline)
        .alert("Revert every list on \(title) to the bundled text?", isPresented: $confirmResetAll) {
            Button("Revert All", role: .destructive) {
                let previous = CardFingerprint.current(kind: kind, id: id, in: repository)
                editStore.resetAllCardEdits(kind, id: id)
                repository.reapplyEdits()
                CardFingerprint.rebaseline(kind: kind, id: id, previous: previous, repository: repository, userData: userData)
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This removes the local content edits for this card.")
        }
    }

    private func fieldRow(_ field: CardField) -> some View {
        let lines = editStore.cardLines(field, kind: kind, id: id)
        let isEdited = editStore.isCardFieldEdited(field, kind: kind, id: id)
        return HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 3) {
                Text(field.displayName)
                    .font(.subheadline.weight(.semibold))
                Text(lines.isEmpty ? "Empty" : "\(lines.count) line\(lines.count == 1 ? "" : "s")")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer(minLength: 8)
            if isEdited {
                Text("EDITED")
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(AppSemanticColor.warningText)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.14), in: Capsule())
            }
        }
        .padding(.vertical, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(field.displayName), \(lines.count) lines\(isEdited ? ", edited" : "")")
    }
}

/// Line-by-line editor for one list on a rescue card or kit.
struct CardFieldEditorView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var editStore: ProcedureEditStore
    @EnvironmentObject private var userData: UserDataStore
    let kind: CardKind
    let id: String
    let field: CardField

    @State private var lines: [String] = []
    @State private var loaded = false
    @State private var confirmRevert = false
    @FocusState private var focusedLine: Int?

    var body: some View {
        List {
            if field.isClinicallyMaterial {
                Section {
                    Label(
                        "Clinically material content. The existing review stays as it is. Exporting will not promote the sign-off until the edit is applied to the bundled content.",
                        systemImage: "exclamationmark.triangle.fill"
                    )
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(AppSemanticColor.warningText)
                    .fixedSize(horizontal: false, vertical: true)
                }
            }

            Section {
                ForEach(Array(lines.enumerated()), id: \.offset) { index, _ in
                    TextField(
                        "Line \(index + 1)",
                        text: Binding(
                            get: { index < lines.count ? lines[index] : "" },
                            set: { if index < lines.count { lines[index] = $0 } }
                        ),
                        axis: .vertical
                    )
                    .focused($focusedLine, equals: index)
                    .font(.body)
                    .accessibilityLabel("\(field.displayName) line \(index + 1)")
                }
                .onDelete { offsets in
                    focusedLine = nil
                    lines.remove(atOffsets: offsets)
                    save()
                }
                .onMove { source, destination in
                    focusedLine = nil
                    lines.move(fromOffsets: source, toOffset: destination)
                    save()
                }

                Button {
                    lines.append("")
                    focusedLine = lines.count - 1
                } label: {
                    Label("Add Line", systemImage: "plus.circle.fill")
                        .frame(minHeight: AppLayout.controlMinHeight)
                }
            } header: {
                Text(field.displayName)
            } footer: {
                Text("Swipe a line to delete it. Blank lines are discarded on save.")
            }

            if editStore.isCardFieldEdited(field, kind: kind, id: id) {
                Section {
                    Button(role: .destructive) {
                        confirmRevert = true
                    } label: {
                        Label("Revert to Bundled Text", systemImage: "arrow.uturn.backward")
                            .frame(minHeight: AppLayout.controlMinHeight)
                    }
                }
            }
        }
        .navigationTitle(field.displayName)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) { EditButton() }
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()
                Button("Done") { focusedLine = nil }
            }
        }
        .onAppear {
            guard !loaded else { return }
            lines = editStore.cardLines(field, kind: kind, id: id)
            loaded = true
        }
        .onDisappear { save() }
        .scrollDismissesKeyboard(.interactively)
        .alert("Revert \(field.displayName) to the bundled text?", isPresented: $confirmRevert) {
            Button("Revert", role: .destructive) {
                let previous = CardFingerprint.current(kind: kind, id: id, in: repository)
                editStore.resetCardField(field, kind: kind, id: id)
                repository.reapplyEdits()
                CardFingerprint.rebaseline(kind: kind, id: id, previous: previous, repository: repository, userData: userData)
                lines = editStore.bundledCardLines(field, kind: kind, id: id)
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This removes the local edit for this list.")
        }
    }

    private var normalizedLines: [String] {
        lines.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
    }

    private func save() {
        guard normalizedLines != editStore.cardLines(field, kind: kind, id: id) else { return }
        let previous = CardFingerprint.current(kind: kind, id: id, in: repository)
        editStore.setCardLines(lines, field: field, kind: kind, id: id)
        repository.reapplyEdits()
        CardFingerprint.rebaseline(kind: kind, id: id, previous: previous, repository: repository, userData: userData)
    }
}

/// Reads a merged card's review fingerprint and keeps your own sign-off
/// current after your own edit, as the procedure editor does.
@MainActor
enum CardFingerprint {
    static func current(kind: CardKind, id: String, in repository: ProcedureRepository) -> (fingerprint: String, version: String)? {
        switch kind {
        case .rescue:
            return repository.rescueCards.first(where: { $0.id == id }).map { ($0.materialFingerprint, $0.version) }
        case .kit:
            return repository.kits.first(where: { $0.id == id }).map { ($0.materialFingerprint, $0.version) }
        }
    }

    static func rebaseline(
        kind: CardKind, id: String, previous: (fingerprint: String, version: String)?,
        repository: ProcedureRepository, userData: UserDataStore
    ) {
        guard let updated = current(kind: kind, id: id, in: repository) else { return }
        userData.rebaselineReviewAfterLocalCardEdit(
            kind: kind, id: id, newFingerprint: updated.fingerprint,
            version: updated.version, previousFingerprint: previous?.fingerprint
        )
    }
}
