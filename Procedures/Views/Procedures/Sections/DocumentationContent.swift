import SwiftUI

struct DocumentationContent: View {
    let procedure: Procedure
    @Binding var noteText: String
    @EnvironmentObject private var userData: UserDataStore
    @FocusState private var notesFocused: Bool
    @State private var showCopied = false
    @State private var copyTask: Task<Void, Never>?
    @State private var saveTask: Task<Void, Never>?

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionCard(title: "Documentation Language", systemImage: "doc.text") {
                VStack(alignment: .leading, spacing: 10) {
                    if procedure.sections.documentation.isEmpty {
                        Text("No documentation language entered yet.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    } else {
                        HStack {
                            Spacer()
                            Button {
                                UIPasteboard.general.string = procedure.sections.documentation.joined(separator: "\n\n")
                                showCopied = true
                                copyTask?.cancel()
                                copyTask = Task { @MainActor in
                                    try? await Task.sleep(for: .seconds(1.5))
                                    guard !Task.isCancelled else { return }
                                    showCopied = false
                                }
                            } label: {
                                Label(showCopied ? "Copied" : "Copy All", systemImage: showCopied ? "checkmark" : "doc.on.doc")
                                    .font(.footnote.weight(.semibold))
                            }
                        }
                        ForEach(Array(procedure.sections.documentation.enumerated()), id: \.offset) { _, line in
                            Text(line)
                                .font(.body)
                                .textSelection(.enabled)
                        }
                    }
                }
            }

            SectionCard(title: "My Local Notes", systemImage: "square.and.pencil") {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Use this for your hospital kit location, attending preferences, or personal reminders. Stored only on device.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                    TextEditor(text: $noteText)
                        .focused($notesFocused)
                        .frame(minHeight: 140)
                        .padding(8)
                        .scrollContentBackground(.hidden)
                        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 12))
                        .toolbar {
                            ToolbarItemGroup(placement: .keyboard) {
                                Spacer()
                                Button("Done") { notesFocused = false }
                            }
                        }
                        .onChange(of: noteText) { _, newValue in
                            saveTask?.cancel()
                            saveTask = Task { @MainActor in
                                try? await Task.sleep(for: .milliseconds(500))
                                guard !Task.isCancelled else { return }
                                userData.setNote(newValue, for: procedure)
                            }
                        }
                }
            }
        }
        .onDisappear {
            copyTask?.cancel()
            saveTask?.cancel()
            userData.setNote(noteText, for: procedure)
        }
    }
}
