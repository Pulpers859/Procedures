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

