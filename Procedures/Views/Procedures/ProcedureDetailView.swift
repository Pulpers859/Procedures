import SwiftUI

struct ProcedureDetailView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @EnvironmentObject private var editStore: ProcedureEditStore
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    let procedure: Procedure
    @State private var selectedSection: ProcedureDetailSection
    @State private var noteText = ""

    /// Scroll anchor for the section selector, so switching sections returns
    /// the reader to the top of the new content.
    private static let selectorAnchor = "procedure.sectionSelector"

    init(procedure: Procedure, initialSection: ProcedureDetailSection? = nil) {
        self.procedure = procedure
        _selectedSection = State(initialValue: initialSection ?? .shiftMode)
    }

    /// The procedure as the repository currently holds it.
    ///
    /// `procedure` is the value that was pushed onto the navigation path, and a
    /// pushed value is frozen: editing a section and tapping Back would leave
    /// this screen rendering the text the clinician had just replaced, which
    /// reads as the edit having failed. Everything below draws from `current`
    /// so an edit is visible the moment it is saved.
    private var current: Procedure {
        repository.procedures.first { $0.id == procedure.id } ?? procedure
    }

    private var relatedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter { $0.relatedProcedureIDs.contains(procedure.id) }
    }

    private var primarySections: [ProcedureDetailSection] {
        [.shiftMode, .equipment, .steps, .complications]
    }

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(
                    alignment: .leading,
                    spacing: AppLayout.sectionSpacing,
                    pinnedViews: [.sectionHeaders]
                ) {
                    header

                    Section {
                        // ComplicationContent (the Rescue tab body) renders its
                        // own full "Open Rescue" card for the same cards, with
                        // an acuity badge the pinned strip doesn't have. Showing
                        // both stacks the identical link twice on the one tab
                        // that exists specifically to reach it.
                        if !relatedRescueCards.isEmpty, selectedSection != .complications {
                            rescueShortcuts
                        }
                        selectedContent
                    } header: {
                        sectionSelector
                            .id(Self.selectorAnchor)
                    }
                }
                .detailContentColumn()
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
            }
            .scrollDismissesKeyboard(.interactively)
            .onChange(of: selectedSection) { _, newSection in
                // Switching sections replaces the content but kept the old
                // scroll offset, so a clinician scrolled deep into Steps who
                // tapped Rescue landed mid-card in unrelated content. VoiceOver
                // additionally got no signal that anything had changed.
                proxy.scrollTo(Self.selectorAnchor, anchor: .top)
                AccessibilityNotification.Announcement(shortTitle(for: newSection)).post()
            }
        }
        .background(Color(.systemGroupedBackground))
        // The full title already renders in `header` below, in full and
        // unabbreviated. An inline nav bar title has to share the bar with
        // the back button and two toolbar icons, so it truncates long
        // titles ("Deep Peroneal Nerve B...") - a degraded second copy of
        // information the reader already has. Leaving it blank keeps the
        // back button and toolbar without repeating (and mangling) the title.
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            if reviewModeEnabled {
                NavigationLink {
                    ProcedureEditorView(procedure: current)
                } label: {
                    Image(systemName: "square.and.pencil")
                }
                .accessibilityLabel("Edit this procedure's content")
            }
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
                    Text(current.category.rawValue)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.secondary)
                    Text(current.title)
                        .font(.title2.weight(.bold))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer()
                VStack(alignment: .trailing, spacing: 6) {
                    difficultyBadge
                    // Always shown, in every state. This page used to read
                    // "DRAFT — not clinically reviewed" even to the clinician who
                    // had signed the procedure off, because it asked the bundled
                    // content and never the reader's own record.
                    ReviewStateChip(
                        state: userData.reviewState(for: current),
                        source: current.source
                    )
                }
            }

            FlowTagView(tags: [current.reviewTime] + current.setting.map(\.rawValue))
        }
    }

    private var difficultyBadge: some View {
        let isHighRisk = current.difficulty == .advanced || current.difficulty == .rareCrash
        return Text(current.difficulty.rawValue.uppercased())
            .font(.caption.weight(.heavy))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .foregroundStyle(isHighRisk ? .orange : .blue)
            .background((isHighRisk ? Color.orange : Color.blue).opacity(0.13), in: Capsule())
            // Without this, VoiceOver reads the raw word alone - "Rare-Crash"
            // read out of context sounds like an acuity signal, not a
            // difficulty rating. AcuityBadge, right below this in the same
            // header, already sets its own equivalent label.
            .accessibilityLabel("Difficulty: \(current.difficulty.rawValue)")
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
                if current.hasVisualAssets {
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
            // shortTitle, not section.rawValue: the collapsed "More" pill
            // echoes back shortTitle after a selection ("Documentation" ->
            // "Chart" read as if a different section had been picked).
            Label(shortTitle(for: section), systemImage: systemImage(for: section))
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
        } else if dynamicTypeSize.isAccessibilitySize {
            // A 220pt-wide card truncates the rescue title at accessibility
            // sizes — on the crash path, where the title is the thing being
            // read. Stack full width instead of scrolling horizontally.
            VStack(spacing: 8) {
                ForEach(relatedRescueCards) { card in
                    rescueButton(card: card)
                }
            }
            .accessibilityLabel("Related rescue cards")
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
                        .lineLimit(dynamicTypeSize.isAccessibilitySize ? nil : 2)
                        .fixedSize(horizontal: false, vertical: true)
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
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Open rescue, \(card.title)")
        }
        .buttonStyle(.plain)
    }

    @ViewBuilder
    private var selectedContent: some View {
        Group {
            switch selectedSection {
            case .shiftMode:
                ShiftModeProcedureContent(procedure: current)
            case .visuals:
                VisualGuideContent(procedure: current)
            case .equipment:
                EquipmentChecklistContent(procedure: current)
            case .steps:
                StepByStepContent(procedure: current)
            case .complications:
                ComplicationContent(procedure: current)
            case .documentation:
                DocumentationContent(procedure: current, noteText: $noteText)
            case .deepReview:
                DeepReviewContent(procedure: current)
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
