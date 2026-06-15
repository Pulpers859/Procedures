import SwiftUI

/// App-wide appearance preference. Stored as a raw string in AppStorage and
/// applied at the root via `.preferredColorScheme`.
enum AppAppearance: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var label: String {
        switch self {
        case .system: return "System"
        case .light: return "Light"
        case .dark: return "Dark"
        }
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .system: return nil
        case .light: return .light
        case .dark: return .dark
        }
    }
}

enum SettingsStorageKey {
    static let appearance = "Procedures.appearance"
    static let defaultSection = "Procedures.defaultSection"
    static let disclaimerAccepted = "Procedures.hasAcceptedClinicalDisclaimer"
}

struct SettingsView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @Environment(\.dismiss) private var dismiss

    @AppStorage(SettingsStorageKey.appearance) private var appearanceRaw = AppAppearance.system.rawValue
    @AppStorage(SettingsStorageKey.defaultSection) private var defaultSectionRaw = ProcedureDetailSection.shiftMode.rawValue
    @AppStorage(SettingsStorageKey.disclaimerAccepted) private var hasAcceptedDisclaimer = false

    @State private var confirmation: DataAction?

    private var appearance: Binding<AppAppearance> {
        Binding(
            get: { AppAppearance(rawValue: appearanceRaw) ?? .system },
            set: { appearanceRaw = $0.rawValue }
        )
    }

    private var defaultSection: Binding<ProcedureDetailSection> {
        Binding(
            get: { ProcedureDetailSection(rawValue: defaultSectionRaw) ?? .shiftMode },
            set: { defaultSectionRaw = $0.rawValue }
        )
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Appearance") {
                    Picker("Theme", selection: appearance) {
                        ForEach(AppAppearance.allCases) { option in
                            Text(option.label).tag(option)
                        }
                    }
                }

                Section {
                    Picker("Open procedures to", selection: defaultSection) {
                        ForEach(ProcedureDetailSection.allCases) { section in
                            Text(section.rawValue).tag(section)
                        }
                    }
                } header: {
                    Text("Procedure Pages")
                } footer: {
                    Text("Choose which tab a procedure opens to by default. Shift Mode is the fast bedside view.")
                }

                Section("Content") {
                    NavigationLink {
                        ContentHealthView()
                    } label: {
                        Label("Content Health", systemImage: "checkmark.seal")
                    }
                }

                Section {
                    Button(role: .destructive) { confirmation = .clearRecents } label: {
                        Label("Clear Recently Viewed", systemImage: "clock.arrow.circlepath")
                    }
                    Button(role: .destructive) { confirmation = .clearFavorites } label: {
                        Label("Clear Saved Procedures", systemImage: "bookmark.slash")
                    }
                    Button(role: .destructive) { confirmation = .clearChecklists } label: {
                        Label("Reset Equipment Checklists", systemImage: "checklist.unchecked")
                    }
                    Button(role: .destructive) { confirmation = .clearNotes } label: {
                        Label("Delete Local Notes", systemImage: "trash")
                    }
                } header: {
                    Text("My Data")
                } footer: {
                    Text("Favorites, recents, checklists, and notes are stored only on this device.")
                }

                Section {
                    Button {
                        hasAcceptedDisclaimer = false
                        dismiss()
                    } label: {
                        Label("Show Disclaimer Again", systemImage: "exclamationmark.shield")
                    }
                } header: {
                    Text("About")
                } footer: {
                    Text("Procedures is an educational review tool for trained clinicians. It does not replace formal training, supervision, credentialing, clinical judgment, or local institutional policy.")
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
            .confirmationDialog(
                confirmation?.title ?? "",
                isPresented: Binding(
                    get: { confirmation != nil },
                    set: { if !$0 { confirmation = nil } }
                ),
                titleVisibility: .visible
            ) {
                if let action = confirmation {
                    Button(action.confirmLabel, role: .destructive) {
                        perform(action)
                    }
                }
            }
        }
    }

    private func perform(_ action: DataAction) {
        switch action {
        case .clearRecents: userData.clearRecents()
        case .clearFavorites: userData.clearFavorites()
        case .clearChecklists: userData.clearAllEquipment()
        case .clearNotes: userData.clearAllNotes()
        }
        confirmation = nil
    }
}

private enum DataAction: Identifiable {
    case clearRecents
    case clearFavorites
    case clearChecklists
    case clearNotes

    var id: String { title }

    var title: String {
        switch self {
        case .clearRecents: return "Clear all recently viewed procedures?"
        case .clearFavorites: return "Remove all saved procedures?"
        case .clearChecklists: return "Reset every equipment checklist?"
        case .clearNotes: return "Delete all local notes?"
        }
    }

    var confirmLabel: String {
        switch self {
        case .clearRecents: return "Clear Recents"
        case .clearFavorites: return "Clear Saved"
        case .clearChecklists: return "Reset Checklists"
        case .clearNotes: return "Delete Notes"
        }
    }
}
