import SwiftUI

struct ProcedureDetailView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    let procedure: Procedure
    @State private var selectedSection: ProcedureDetailSection
    @State private var noteText = ""

    init(procedure: Procedure, initialSection: ProcedureDetailSection? = nil) {
        self.procedure = procedure
        _selectedSection = State(initialValue: initialSection ?? .shiftMode)
    }

    private var relatedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter { $0.relatedProcedureIDs.contains(procedure.id) }
    }

    private var primarySections: [ProcedureDetailSection] {
        [.shiftMode, .equipment, .steps, .complications]
    }

    var body: some View {
        ScrollView {
            LazyVStack(
                alignment: .leading,
                spacing: AppLayout.sectionSpacing,
                pinnedViews: [.sectionHeaders]
            ) {
                header

                Section {
                    if !relatedRescueCards.isEmpty {
                        rescueShortcuts
                    }
                    selectedContent
                } header: {
                    sectionSelector
                }
            }
            .detailContentColumn()
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
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
        VStack(alignment: .leading, spacing: 10) {
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
                VStack(alignment: .trailing, spacing: 6) {
                    difficultyBadge
                    if !procedure.reviewer.isClinicallyReviewed {
                        Label(
                            procedure.source == .aiDraft ? "DRAFT — not clinically reviewed" : "Needs review",
                            systemImage: "exclamationmark.shield"
                        )
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.orange)
                        .multilineTextAlignment(.trailing)
                        .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }

            FlowTagView(tags: [procedure.reviewTime] + procedure.setting.map(\.rawValue))
        }
    }

    private var difficultyBadge: some View {
        let isHighRisk = procedure.difficulty == .advanced || procedure.difficulty == .rareCrash
        return Text(procedure.difficulty.rawValue.uppercased())
            .font(.caption.weight(.heavy))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .foregroundStyle(isHighRisk ? .orange : .blue)
            .background((isHighRisk ? Color.orange : Color.blue).opacity(0.13), in: Capsule())
    }

    private var sectionSelector: some View {
        Group {
            if dynamicTypeSize.isAccessibilitySize {
                ScrollView(.horizontal, showsIndicators: false) {
                    selectorButtons
                }
            } else {
                selectorButtons
            }
        }
        .padding(4)
        .background(.bar, in: RoundedRectangle(cornerRadius: AppLayout.controlRadius, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: AppLayout.controlRadius, style: .continuous)
                .stroke(.secondary.opacity(0.12), lineWidth: 1)
        )
        .padding(.vertical, 6)
        .background(Color(.systemGroupedBackground))
        .sensoryFeedback(.selection, trigger: selectedSection)
        .accessibilityLabel("Procedure sections")
    }

    private var selectorButtons: some View {
        HStack(spacing: 4) {
            ForEach(primarySections) { section in
                sectionButton(section)
            }

            Menu {
                if procedure.hasVisualAssets {
                    sectionMenuButton(.visuals)
                }
                sectionMenuButton(.documentation)
                sectionMenuButton(.deepReview)
            } label: {
                let secondarySelected = !primarySections.contains(selectedSection)
                sectionLabel(
                    title: secondarySelected ? shortTitle(for: selectedSection) : "More",
                    systemImage: secondarySelected ? systemImage(for: selectedSection) : "ellipsis.circle",
                    isSelected: secondarySelected
                )
            }
            .accessibilityLabel("More procedure sections")
            .accessibilityAddTraits(!primarySections.contains(selectedSection) ? .isSelected : [])
        }
    }

    private func sectionButton(_ section: ProcedureDetailSection) -> some View {
        Button {
            select(section)
        } label: {
            sectionLabel(
                title: shortTitle(for: section),
                systemImage: systemImage(for: section),
                isSelected: selectedSection == section
            )
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(selectedSection == section ? .isSelected : [])
    }

    private func sectionMenuButton(_ section: ProcedureDetailSection) -> some View {
        Button {
            select(section)
        } label: {
            Label(section.rawValue, systemImage: systemImage(for: section))
        }
    }

    private func sectionLabel(title: String, systemImage: String, isSelected: Bool) -> some View {
        VStack(spacing: 3) {
            Image(systemName: systemImage)
                .font(.subheadline.weight(.semibold))
            Text(title)
                .font(.caption2.weight(.semibold))
                .lineLimit(1)
        }
        .foregroundStyle(isSelected ? Color.blue : Color.primary)
        .frame(
            minWidth: dynamicTypeSize.isAccessibilitySize ? 76 : nil,
            maxWidth: dynamicTypeSize.isAccessibilitySize ? nil : .infinity,
            minHeight: 48
        )
        .background(isSelected ? Color.blue.opacity(0.12) : Color.clear, in: RoundedRectangle(cornerRadius: AppLayout.controlRadius, style: .continuous))
        .contentShape(Rectangle())
    }

    @ViewBuilder
    private var rescueShortcuts: some View {
        if let card = relatedRescueCards.first, relatedRescueCards.count == 1 {
            rescueButton(card: card)
        } else {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(relatedRescueCards) { card in
                        rescueButton(card: card)
                            .frame(width: 220)
                    }
                }
            }
            .accessibilityLabel("Related rescue cards")
        }
    }

    private func rescueButton(card: ComplicationRescueCard) -> some View {
        NavigationLink {
            RescueCardDetailView(card: card)
        } label: {
            HStack(spacing: 10) {
                Image(systemName: "lifepreserver.fill")
                    .foregroundStyle(.red)
                VStack(alignment: .leading, spacing: 2) {
                    Text("Open rescue")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.secondary)
                    Text(card.title)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.primary)
                        .lineLimit(2)
                }
                Spacer(minLength: 8)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
            }
            .padding(.horizontal, 12)
            .frame(maxWidth: .infinity, minHeight: AppLayout.controlMinHeight, alignment: .leading)
            .background(Color.red.opacity(0.09), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous)
                    .stroke(Color.red.opacity(0.22), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
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
        .transition(reduceMotion ? .identity : .opacity)
    }

    private func select(_ section: ProcedureDetailSection) {
        withAnimation(reduceMotion ? nil : .snappy) {
            selectedSection = section
        }
    }

    private func shortTitle(for section: ProcedureDetailSection) -> String {
        switch section {
        case .shiftMode: return "Brief"
        case .visuals: return "Visual"
        case .equipment: return "Setup"
        case .steps: return "Steps"
        case .complications: return "Rescue"
        case .documentation: return "Chart"
        case .deepReview: return "Review"
        }
    }

    private func systemImage(for section: ProcedureDetailSection) -> String {
        switch section {
        case .shiftMode: return "bolt.fill"
        case .visuals: return "photo"
        case .equipment: return "checklist"
        case .steps: return "list.number"
        case .complications: return "lifepreserver"
        case .documentation: return "doc.text"
        case .deepReview: return "books.vertical"
        }
    }
}
