import SwiftUI

struct DeepReviewContent: View {
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    var body: some View {
        VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
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
            DisclosureSectionCard(title: showGovernanceCopy ? "References + Disclaimer" : "References", systemImage: "books.vertical") {
                VStack(alignment: .leading, spacing: 8) {
                    if procedure.sections.references.isEmpty {
                        Text("No references entered yet. This should block release-quality content approval.")
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(AppSemanticColor.warningText)
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
                SectionCard(title: "Review", systemImage: "checkmark.shield") {
                    LocalReviewPanel(
                        sourceStatus: procedure.reviewer,
                        sourceOrigin: procedure.source,
                        sourceLastReviewed: procedure.lastReviewed,
                        sourceVersion: procedure.version,
                        localReviewRecord: userData.localReviewRecord(for: procedure),
                        materialState: userData.reviewContentState(for: procedure),
                        markReviewed: { userData.markReviewed(procedure) },
                        markNeedsEdits: { userData.setReviewDisposition(.needsEdits, for: procedure) },
                        deferReview: { userData.setReviewDisposition(.deferred, for: procedure) },
                        clearReview: { userData.clearReview(for: procedure) }
                    )
                }
            }
        }
    }

    private var showGovernanceCopy: Bool {
        reviewModeEnabled || !hideGovernanceCopy
    }
}
