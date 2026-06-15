import SwiftUI
import UIKit

struct ProcedureDetailView: View {
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    @State private var selectedSection: ProcedureDetailSection
    @State private var noteText = ""

    init(procedure: Procedure) {
        self.procedure = procedure
        let stored = UserDefaults.standard.string(forKey: SettingsStorageKey.defaultSection)
        _selectedSection = State(initialValue: ProcedureDetailSection(rawValue: stored ?? "") ?? .shiftMode)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header
                sectionSelector
                selectedContent
            }
            .padding()
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle(procedure.title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            Button {
                userData.toggleFavorite(procedure)
            } label: {
                Image(systemName: userData.isFavorite(procedure) ? "bookmark.fill" : "bookmark")
            }
            .accessibilityLabel(userData.isFavorite(procedure) ? "Remove favorite" : "Add favorite")
        }
        .sensoryFeedback(.impact(weight: .light), trigger: userData.isFavorite(procedure))
        .onAppear {
            userData.markRecentlyViewed(procedure)
            noteText = userData.note(for: procedure)
        }
        .navigationDestination(for: ComplicationRescueCard.self) { card in
            RescueCardDetailView(card: card)
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top, spacing: 12) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(procedure.category.rawValue)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.secondary)
                    Text(procedure.title)
                        .font(.title2.weight(.bold))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer()
                riskBadge
            }

            FlowTagView(tags: [procedure.difficulty.rawValue, procedure.reviewTime] + procedure.setting.map(\.rawValue))

            if let visual = procedure.bundledVisual {
                ProcedureVisualCard(asset: visual.asset, image: visual.image)
            }
        }
    }

    private var riskBadge: some View {
        let isHighRisk = procedure.difficulty == .advanced || procedure.difficulty == .rareCrash
        return Text(isHighRisk ? "HIGH RISK" : "REVIEW")
            .font(.caption.weight(.heavy))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .foregroundStyle(isHighRisk ? .orange : .blue)
            .background((isHighRisk ? Color.orange : Color.blue).opacity(0.13), in: Capsule())
    }

    private var sectionSelector: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(ProcedureDetailSection.allCases) { section in
                    Button {
                        withAnimation(.snappy) { selectedSection = section }
                    } label: {
                        Text(section.rawValue)
                            .font(.subheadline.weight(.semibold))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .foregroundStyle(selectedSection == section ? .white : .primary)
                            .background(selectedSection == section ? Color.blue : Color(.secondarySystemGroupedBackground), in: Capsule())
                    }
                    .buttonStyle(.plain)
                    .accessibilityAddTraits(selectedSection == section ? .isSelected : [])
                }
            }
            .padding(.vertical, 2)
        }
        .sensoryFeedback(.selection, trigger: selectedSection)
        .accessibilityLabel("Procedure sections")
    }

    @ViewBuilder
    private var selectedContent: some View {
        switch selectedSection {
        case .shiftMode:
            ShiftModeProcedureContent(procedure: procedure)
        case .equipment:
            EquipmentChecklistContent(procedure: procedure)
        case .steps:
            StepByStepContent(procedure: procedure)
        case .complications:
            ComplicationContent(procedure: procedure)
        case .documentation:
            DocumentationContent(procedure: procedure, noteText: $noteText)
        case .deepReview:
            DeepReviewContent(procedure: procedure)
        }
    }
}

struct ShiftModeProcedureContent: View {
    let procedure: Procedure

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            CriticalWarningCard(title: "Need-to-know before you walk in", items: procedure.sections.shiftMode)

            if !procedure.sections.troubleshooting.isEmpty {
                SectionCard(title: "Failure Plan", systemImage: "wrench.and.screwdriver") {
                    BulletListView(items: procedure.sections.troubleshooting)
                }
            }

            if !procedure.sections.seniorPearls.isEmpty {
                SectionCard(title: "Senior Pearls", systemImage: "quote.bubble") {
                    BulletListView(items: procedure.sections.seniorPearls)
                }
            }
        }
    }
}

struct EquipmentChecklistContent: View {
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    @State private var showingResetConfirmation = false

    var body: some View {
        SectionCard(title: "Room + Equipment Checklist", systemImage: "checklist") {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("Tap items as they are physically in the room.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button("Reset") {
                        showingResetConfirmation = true
                    }
                    .font(.footnote.weight(.semibold))
                    .confirmationDialog("Reset all equipment items?", isPresented: $showingResetConfirmation, titleVisibility: .visible) {
                        Button("Reset Checklist", role: .destructive) {
                            userData.resetEquipment(for: procedure)
                        }
                    }
                }

                ForEach(procedure.sections.equipment, id: \.self) { item in
                    ChecklistRow(
                        text: item,
                        isChecked: userData.isEquipmentChecked(item, for: procedure),
                        action: { userData.toggleEquipment(item, for: procedure) }
                    )
                }
            }
        }
    }
}

struct StepByStepContent: View {
    let procedure: Procedure

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            if !procedure.sections.positioning.isEmpty {
                SectionCard(title: "Positioning", systemImage: "person.crop.rectangle") {
                    BulletListView(items: procedure.sections.positioning)
                }
            }

            if !procedure.sections.steps.isEmpty {
                SectionCard(title: "Steps", systemImage: "list.number") {
                    NumberedListView(items: procedure.sections.steps)
                }
            }

            if !procedure.sections.confirmation.isEmpty {
                SectionCard(title: "Confirmation", systemImage: "checkmark.seal") {
                    BulletListView(items: procedure.sections.confirmation)
                }
            }
        }
    }
}

struct ComplicationContent: View {
    @EnvironmentObject private var repository: ProcedureRepository
    let procedure: Procedure

    private var relatedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter { $0.relatedProcedureIDs.contains(procedure.id) }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            CriticalWarningCard(title: "Complications to anticipate", items: procedure.sections.complications)

            if !relatedRescueCards.isEmpty {
                SectionCard(title: "Rescue Cards", systemImage: "lifepreserver.fill") {
                    VStack(alignment: .leading, spacing: 10) {
                        ForEach(relatedRescueCards) { card in
                            NavigationLink(value: card) {
                                HStack {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(card.title)
                                            .font(.subheadline.weight(.semibold))
                                        Text(card.trigger.first ?? "")
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                            .lineLimit(1)
                                    }
                                    Spacer()
                                    Text(card.acuity.rawValue.uppercased())
                                        .font(.caption2.weight(.heavy))
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .foregroundStyle(card.acuity == .crash ? .red : .orange)
                                        .background((card.acuity == .crash ? Color.red : Color.orange).opacity(0.14), in: Capsule())
                                    Image(systemName: "chevron.right")
                                        .font(.caption.weight(.semibold))
                                        .foregroundStyle(.secondary)
                                }
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }

            if !procedure.sections.troubleshooting.isEmpty {
                SectionCard(title: "Immediate Rescue Moves", systemImage: "lifepreserver") {
                    BulletListView(items: procedure.sections.troubleshooting)
                }
            }

            if !procedure.sections.aftercare.isEmpty {
                SectionCard(title: "Aftercare", systemImage: "cross.case") {
                    BulletListView(items: procedure.sections.aftercare)
                }
            }
        }
    }
}

struct DocumentationContent: View {
    let procedure: Procedure
    @Binding var noteText: String
    @EnvironmentObject private var userData: UserDataStore
    @State private var showCopied = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionCard(title: "Documentation Language", systemImage: "doc.text") {
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Spacer()
                        Button {
                            UIPasteboard.general.string = procedure.sections.documentation.joined(separator: "\n\n")
                            showCopied = true
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { showCopied = false }
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

            SectionCard(title: "My Local Notes", systemImage: "square.and.pencil") {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Use this for your hospital kit location, attending preferences, or personal reminders. Stored only on device.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                    TextEditor(text: $noteText)
                        .frame(minHeight: 140)
                        .padding(8)
                        .scrollContentBackground(.hidden)
                        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 12))
                        .onChange(of: noteText) { _, newValue in
                            userData.setNote(newValue, for: procedure)
                        }
                }
            }
        }
    }
}

struct DeepReviewContent: View {
    let procedure: Procedure

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
            SectionCard(title: "References + Disclaimer", systemImage: "books.vertical") {
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
                    Divider().padding(.vertical, 4)
                    Text("Educational review for trained clinicians. Does not replace formal training, supervision, credentialing, clinical judgment, or local institutional policy.")
                        .font(.footnote.weight(.semibold))
                        .foregroundStyle(.secondary)
                }
            }

            SectionCard(title: "Clinical Governance", systemImage: "checkmark.shield") {
                VStack(spacing: 8) {
                    MetadataRow(icon: "calendar", title: "Last reviewed", value: procedure.lastReviewed)
                    MetadataRow(icon: "number", title: "Content version", value: procedure.version)
                }
            }
        }
    }
}


/// Shows a real bundled landmark/probe/danger-zone image. Renders nothing when
/// no image is bundled, so the procedure page never carries a dead placeholder.
struct ProcedureVisualCard: View {
    let asset: ProcedureVisualAsset
    let image: UIImage

    var body: some View {
        SectionCard(title: "Visual Landmark", systemImage: "photo.on.rectangle.angled") {
            VStack(alignment: .leading, spacing: 10) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: .infinity)
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    .accessibilityLabel(asset.title)

                Text(asset.title)
                    .font(.subheadline.weight(.semibold))

                if !asset.subtitle.isEmpty {
                    Text(asset.subtitle)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }

                if let warning = asset.clinicalWarning, !warning.isEmpty {
                    Label(warning, systemImage: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundStyle(.orange)
                        .fixedSize(horizontal: false, vertical: true)
                }

                if !asset.caption.isEmpty {
                    Text(asset.caption)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }
}

extension Procedure {
    /// The primary visual asset paired with its bundled image, if one actually
    /// ships in the app bundle. Returns nil when there is no real image to show.
    var bundledVisual: (asset: ProcedureVisualAsset, image: UIImage)? {
        guard let asset = primaryVisualAsset,
              let assetName = asset.assetName, !assetName.isEmpty,
              let image = ProcedureVisualLoader.image(named: assetName) else {
            return nil
        }
        return (asset, image)
    }
}

enum ProcedureVisualLoader {
    static func image(named assetName: String) -> UIImage? {
        if let image = UIImage(named: assetName) {
            return image
        }

        let url = Bundle.main.url(forResource: assetName, withExtension: nil)
            ?? Bundle.main.url(forResource: assetName, withExtension: "png")
            ?? Bundle.main.url(forResource: assetName, withExtension: "jpg")
            ?? Bundle.main.url(forResource: assetName, withExtension: "jpeg")

        guard let url else { return nil }
        return UIImage(contentsOfFile: url.path)
    }
}
