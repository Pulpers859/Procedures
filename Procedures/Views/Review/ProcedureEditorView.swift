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
    let procedure: Procedure

    @State private var confirmResetAll = false

    var body: some View {
        List {
            Section {
                Text("Your edits are saved on this device and replace the bundled text everywhere in the app. Nothing that shipped is overwritten — any section can be reverted.")
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
        .confirmationDialog(
            "Revert every section of \(procedure.title) to the bundled text?",
            isPresented: $confirmResetAll,
            titleVisibility: .visible
        ) {
            Button("Revert All", role: .destructive) {
                editStore.resetAllEdits(for: procedure)
                repository.reapplyEdits()
            }
        }
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
    @Environment(\.dismiss) private var dismiss
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
                        "This is clinically material content. Changing it will flag anyone who already reviewed this procedure to take another look.",
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
                    lines.remove(atOffsets: offsets)
                    save()
                }
                .onMove { source, destination in
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
                Text("Swipe a line to delete it. Blank lines are discarded when you save.")
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
        .confirmationDialog(
            "Revert \(section.displayName) to the bundled text?",
            isPresented: $confirmRevert,
            titleVisibility: .visible
        ) {
            Button("Revert", role: .destructive) {
                editStore.resetSection(section, in: procedure)
                repository.reapplyEdits()
                // Read the baseline from the store, not from `procedure`: the
                // repository publishes merged content, so this copy still
                // carries the edit that was just discarded.
                lines = editStore.bundledLines(section, in: procedure)
            }
        }
    }

    private func save() {
        editStore.setLines(lines, for: section, in: procedure)
        repository.reapplyEdits()
    }
}
