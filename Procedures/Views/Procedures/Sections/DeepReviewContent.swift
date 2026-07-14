import SwiftUI

struct DeepReviewContent: View {
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    @Binding var noteText: String
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false
    @FocusState private var notesFocused: Bool
    @State private var saveTask: Task<Void, Never>?

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            if !procedure.sections.indications.isEmpty {
                SectionCard(title: "Indications", systemImage: "target") { BulletListView(items: procedure.sections.indications) }
            }
            if !procedure.sections.contraindications.isEmpty {
                SectionCard(title: "Contraindications / Cautions", systemImage: "hand.raised") { BulletListView(items: procedure.sections.contraindications) }
            }
            if !procedure.sections.anatomy.isEmpty {
                SectionCard(title: "Anatomy / Landmarks", systemImage: "figure.stand") { BulletListView(items: procedure.sections.anatomy) }
            }
            if !procedure.sections.ultrasound.isEmpty {
                SectionCard(title: "Ultrasound Guidance", systemImage: "waveform.path.ecg.rectangle") { BulletListView(items: procedure.sections.ultrasound) }
            }
            SectionCard(title: showGovernanceCopy ? "References + Disclaimer" : "References", systemImage: "books.vertical") {
                VStack(alignment: .leading, spacing: 8) {
                    if procedure.sections.references.isEmpty {
                        Text("No references entered yet. This should block release-quality content approval.")
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(.orange)
                    } else {
                        ForEach(Array(procedure.sections.references.enumerated()), id: \.offset) { _, reference in
                            Text(reference)
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                                .textSelection(.enabled)
                        }
                    }
                    if showGovernanceCopy {
                        Divider().padding(.vertical, 4)
                        Text(AppConstants.shortDisclaimer)
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(.secondary)
                    }
                }
            }

            if reviewModeEnabled {
                SectionCard(title: "My Review", systemImage: "checkmark.shield") {
                    LocalReviewPanel(
                        sourceStatus: procedure.reviewer,
                        sourceLastReviewed: procedure.lastReviewed,
                        sourceVersion: procedure.version,
                        localReviewRecord: userData.localReviewRecord(for: procedure),
                        markReviewed: { userData.markReviewed(procedure) },
                        markNeedsEdits: { userData.setReviewDisposition(.needsEdits, for: procedure) },
                        deferReview: { userData.setReviewDisposition(.deferred, for: procedure) },
                        clearReview: { userData.clearReview(for: procedure) }
                    )
                }

                SectionCard(title: "My Edit Notes", systemImage: "square.and.pencil") {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Capture corrections, source links, local practice changes, or anything you want folded into the bundled content later. Stored only on this device.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                        TextEditor(text: $noteText)
                            .focused($notesFocused)
                            .frame(minHeight: 120)
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
        }
        .onDisappear {
            saveTask?.cancel()
            userData.setNote(noteText, for: procedure)
        }
    }

    private var showGovernanceCopy: Bool {
        reviewModeEnabled || !hideGovernanceCopy
    }
}
