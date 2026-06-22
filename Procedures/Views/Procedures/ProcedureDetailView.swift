import SwiftUI
import UIKit

struct ProcedureDetailView: View {
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    @State private var selectedSection: ProcedureDetailSection
    @State private var noteText = ""

    init(procedure: Procedure, initialSection: ProcedureDetailSection? = nil) {
        self.procedure = procedure
        let stored = UserDefaults.standard.string(forKey: SettingsStorageKey.defaultSection)
        let defaultSection = ProcedureDetailSection(rawValue: stored ?? "") ?? .shiftMode
        _selectedSection = State(initialValue: initialSection ?? defaultSection)
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
        // Navigation destinations are registered once at each tab's NavigationStack
        // root (see GuideHomeView, ProcedureListView, KitsHomeView, SavedView,
        // ComplicationsHomeView). Declaring them here too would create duplicate
        // destinations for the same type in one stack, which makes SwiftUI route
        // links to the wrong screen.
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

    private var availableSections: [ProcedureDetailSection] {
        ProcedureDetailSection.allCases.filter { section in
            if section == .visuals { return procedure.hasVisualAssets }
            return true
        }
    }

    private var sectionSelector: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(availableSections) { section in
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
        Group {
            switch selectedSection {
            case .shiftMode:
                ShiftModeProcedureContent(procedure: procedure)
            case .visuals:
                VisualGuideContent(procedure: procedure)
            case .equipment:
                EquipmentChecklistContent(procedure: procedure)
            case .steps:
                StepByStepContent(procedure: procedure)
            case .complications:
                ComplicationContent(procedure: procedure)
            case .documentation:
                DocumentationContent(procedure: procedure, noteText: $noteText)
            case .deepReview:
                DeepReviewContent(procedure: procedure, noteText: $noteText)
            }
        }
        .id(selectedSection)
        .transition(.opacity.combined(with: .move(edge: .bottom)))
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
                        // Procedure detail can be opened from multiple tab stacks.
                        // Use an explicit destination so rescue links work the same
                        // regardless of which stack presented this screen.
                        ForEach(relatedRescueCards) { card in
                            NavigationLink {
                                RescueCardDetailView(card: card)
                            } label: {
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
                                        .foregroundStyle(card.acuity.tintColor)
                                        .background(card.acuity.tintColor.opacity(0.14), in: Capsule())
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


// MARK: - Visual Guide Content

struct VisualGuideContent: View {
    let procedure: Procedure

    private var assets: [ProcedureVisualAsset] {
        procedure.visualAssets ?? []
    }

    var body: some View {
        if assets.isEmpty {
            SectionCard(title: "Visual Guide", systemImage: "photo.on.rectangle.angled") {
                Text("No visual guides for this procedure yet.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        } else {
            VStack(alignment: .leading, spacing: 16) {
                ForEach(assets) { asset in
                    VisualAssetCard(asset: asset)
                }
            }
        }
    }
}

struct VisualAssetCard: View {
    let asset: ProcedureVisualAsset
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    private var kindTint: Color {
        switch asset.kind {
        case .landmark: return .blue
        case .probePosition: return .cyan
        case .dangerZone: return .red
        case .confirmation: return .green
        case .setup: return .purple
        }
    }

    private var kindIcon: String {
        switch asset.kind {
        case .landmark: return "mappin.and.ellipse"
        case .probePosition: return "dot.viewfinder"
        case .dangerZone: return "exclamationmark.triangle.fill"
        case .confirmation: return "checkmark.seal.fill"
        case .setup: return "tray.2.fill"
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Kind badge header
            HStack(spacing: 8) {
                Image(systemName: kindIcon)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(kindTint)
                Text(asset.kind.rawValue.uppercased())
                    .font(.caption2.weight(.heavy))
                    .foregroundStyle(kindTint)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.top, 14)
            .padding(.bottom, 10)

            // Image or schematic placeholder
            if let image = ProcedureVisualLoader.image(for: asset) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: .infinity)
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                    .padding(.horizontal, 16)
                    .padding(.bottom, 12)
                    .accessibilityLabel(asset.title)
            } else {
                SchematicPlaceholder(asset: asset, tint: kindTint)
                    .padding(.horizontal, 16)
                    .padding(.bottom, 12)
            }

            // Title + subtitle
            VStack(alignment: .leading, spacing: 4) {
                Text(asset.title)
                    .font(.subheadline.weight(.semibold))
                Text(asset.subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(.horizontal, 16)

            // Clinical warning
            if showGovernanceCopy, let warning = asset.clinicalWarning, !warning.isEmpty {
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundStyle(.orange)
                    Text(warning)
                        .font(.caption)
                        .foregroundStyle(.orange)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
            }

            // Caption
            if !asset.caption.isEmpty {
                Text(asset.caption)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 16)
                    .padding(.top, 6)
            }

            Spacer().frame(height: 14)
        }
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(kindTint.opacity(0.25), lineWidth: 1)
        )
    }

    private var showGovernanceCopy: Bool {
        reviewModeEnabled || !hideGovernanceCopy
    }
}

struct SchematicPlaceholder: View {
    let asset: ProcedureVisualAsset
    let tint: Color

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: asset.systemImage ?? "photo")
                .font(.system(size: 44, weight: .medium))
                .foregroundStyle(tint.opacity(0.7))
                .frame(width: 80, height: 80)
                .background(tint.opacity(0.08), in: RoundedRectangle(cornerRadius: 20, style: .continuous))

            Text("Illustration Pending")
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
                .padding(.horizontal, 10)
                .padding(.vertical, 4)
                .background(Color(.tertiarySystemFill), in: Capsule())
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 20)
        .background(tint.opacity(0.04), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
        .accessibilityLabel("\(asset.kind.rawValue) diagram: \(asset.title). Illustration pending.")
    }
}

// MARK: - Header visual (only shows when a real image is bundled)

extension Procedure {
    var bundledVisual: (asset: ProcedureVisualAsset, image: UIImage)? {
        guard let asset = primaryVisualAsset,
              let image = ProcedureVisualLoader.image(for: asset) else {
            return nil
        }
        return (asset, image)
    }

    var hasVisualAssets: Bool {
        guard let assets = visualAssets else { return false }
        return !assets.isEmpty
    }
}

struct ProcedureVisualCard: View {
    let asset: ProcedureVisualAsset
    let image: UIImage
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(uiImage: image)
                .resizable()
                .scaledToFit()
                .frame(maxWidth: .infinity)
                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                .accessibilityLabel(asset.title)

            Text(asset.title)
                .font(.subheadline.weight(.semibold))

            if showGovernanceCopy, let warning = asset.clinicalWarning, !warning.isEmpty {
                Label(warning, systemImage: "exclamationmark.triangle.fill")
                    .font(.caption)
                    .foregroundStyle(.orange)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(.secondary.opacity(0.12), lineWidth: 1)
        )
    }

    private var showGovernanceCopy: Bool {
        reviewModeEnabled || !hideGovernanceCopy
    }
}

enum ProcedureVisualLoader {
    static func image(for asset: ProcedureVisualAsset) -> UIImage? {
        guard let assetName = asset.assetName, !assetName.isEmpty else { return nil }

        for name in [assetName, "Visuals/\(assetName)"] {
            if let image = UIImage(named: name) {
                return image
            }
        }

        let name = (assetName as NSString).deletingPathExtension
        let ext = (assetName as NSString).pathExtension
        let extensions = ext.isEmpty ? [nil, "png", "jpg", "jpeg"] : [ext]
        let subdirectories: [String?] = [nil, "Visuals"]

        for subdirectory in subdirectories {
            for itemExtension in extensions {
                if let url = Bundle.main.url(forResource: ext.isEmpty ? assetName : name, withExtension: itemExtension, subdirectory: subdirectory),
                   let image = UIImage(contentsOfFile: url.path) {
                    return image
                }
            }
        }

        return nil
    }
}
