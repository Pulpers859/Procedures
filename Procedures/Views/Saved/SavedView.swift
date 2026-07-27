import SwiftUI

private enum SavedSection: String, CaseIterable, Identifiable {
    case favorites = "Favorites"
    case recents = "Recents"
    case notes = "Notes"

    var id: String { rawValue }
}

struct SavedView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @SceneStorage("Procedures.selectedSavedSection") private var selectedSectionRaw = SavedSection.favorites.rawValue

    private var sectionPicker: some View {
        Picker("Saved section", selection: selectedSection) {
            ForEach(SavedSection.allCases) { section in
                Text(section.rawValue).tag(section)
            }
        }
    }

    private var selectedSection: Binding<SavedSection> {
        Binding(
            get: { SavedSection(rawValue: selectedSectionRaw) ?? .favorites },
            set: { selectedSectionRaw = $0.rawValue }
        )
    }

    private var favorites: [Procedure] {
        repository.procedures.filter { userData.favoriteIDs.contains($0.id) }
    }

    private var recents: [Procedure] {
        userData.recentIDs.compactMap { repository.procedure(withID: $0) }
    }

    private var proceduresWithNotes: [Procedure] {
        repository.procedures.filter { !userData.note(for: $0).trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    // A segmented picker neither reflows nor scrolls, so at
                    // accessibility sizes the only navigation control on this
                    // tab truncates to unreadable stubs. The two picker styles
                    // are distinct types, so this branches on whole views.
                    if dynamicTypeSize.isAccessibilitySize {
                        sectionPicker.pickerStyle(.menu)
                    } else {
                        sectionPicker.pickerStyle(.segmented)
                    }
                }
                .listRowBackground(Color.clear)

                selectedContent

                if !hideGovernanceCopy {
                    Section("About") {
                        Text(AppConstants.clinicalDisclaimer)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Saved")
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            // ProcedureDetailView surfaces rescue-card links, so this stack must
            // resolve them at the root.
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
            .navigationDestination(for: Kit.self) { kit in
                KitDetailView(kit: kit)
            }
        }
    }

    @ViewBuilder
    private var selectedContent: some View {
        switch selectedSection.wrappedValue {
        case .favorites:
            Section("Favorites") {
                if favorites.isEmpty {
                    emptyRow("No saved procedures")
                } else {
                    ForEach(favorites) { procedure in
                        NavigationLink(value: procedure) {
                            ProcedureCard(procedure: procedure, isFavorite: true)
                        }
                    }
                }
            }
        case .recents:
            Section("Recently Viewed") {
                if recents.isEmpty {
                    emptyRow("No recent procedures")
                } else {
                    ForEach(recents) { procedure in
                        NavigationLink(value: procedure) {
                            ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                        }
                    }
                }
            }
        case .notes:
            Section("Local Notes") {
                if proceduresWithNotes.isEmpty {
                    emptyRow("No local notes")
                } else {
                    ForEach(proceduresWithNotes) { procedure in
                        NavigationLink(value: procedure) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(procedure.title)
                                    .font(.headline)
                                Text(userData.note(for: procedure))
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                                    .lineLimit(2)
                            }
                        }
                    }
                }
            }
        }
    }

    private func emptyRow(_ text: String) -> some View {
        Text(text)
            .foregroundStyle(.secondary)
    }
}
