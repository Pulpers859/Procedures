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
    static let hideGovernanceCopy = "Procedures.hideGovernanceCopy"
    static let reviewModeEnabled = "Procedures.reviewModeEnabled"
}

/// Settings lived only in the Guide toolbar, so a clinician on any other tab
/// had to switch tabs to reach appearance, Clinical Mode, or Review Center.
/// It presents as a sheet, so it costs no navigation-stack complexity.
struct SettingsToolbarModifier: ViewModifier {
    @State private var showingSettings = false

    func body(content: Content) -> some View {
        content
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingSettings = true
                    } label: {
                        Image(systemName: "gearshape")
                    }
                    .accessibilityLabel("Settings")
                }
            }
            .sheet(isPresented: $showingSettings) {
                SettingsView()
            }
    }
}

extension View {
    func settingsToolbar() -> some View { modifier(SettingsToolbarModifier()) }
}

struct SettingsView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @EnvironmentObject private var editStore: ProcedureEditStore
    @Environment(\.dismiss) private var dismiss

    @AppStorage(SettingsStorageKey.appearance) private var appearanceRaw = AppAppearance.system.rawValue
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    @State private var confirmation: DataAction?

    private var appearance: Binding<AppAppearance> {
        Binding(
            get: { AppAppearance(rawValue: appearanceRaw) ?? .system },
            set: { appearanceRaw = $0.rawValue }
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
                    Toggle("Clinical Mode", isOn: $hideGovernanceCopy)
                } header: {
                    Text("Procedure Pages")
                } footer: {
                    Text("Clinical Mode hides editorial metadata and review controls. Clinical warnings and the first-run acknowledgment always remain visible.")
                }

                Section {
                    Toggle("Show review tools", isOn: $reviewModeEnabled)
                    NavigationLink {
                        ReviewCenterView()
                    } label: {
                        Label("Open Review Center", systemImage: "checkmark.seal")
                    }
                } header: {
                    Text("Review Mode")
                } footer: {
                    Text("Review Center stays in Settings so the bedside tab bar remains stable.")
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
                    Button(role: .destructive) { confirmation = .clearKitChecklists } label: {
                        Label("Reset Kit Room-Setup Checklists", systemImage: "shippingbox")
                    }
                    Button(role: .destructive) { confirmation = .clearNotes } label: {
                        Label("Delete Local Notes", systemImage: "trash")
                    }
                    Button(role: .destructive) { confirmation = .clearReviews } label: {
                        Label("Clear Review Marks", systemImage: "checkmark.seal")
                    }
                    // The only local data that overrides *clinical text*, and
                    // the only kind this screen could not clear. The store had
                    // a resetEverything() with no call sites; the sole removal
                    // path was per-procedure, inside Review Mode.
                    if editStore.editedProcedureCount > 0 {
                        Button(role: .destructive) { confirmation = .clearEdits } label: {
                            Label("Discard All Content Edits", systemImage: "arrow.uturn.backward")
                        }
                    }
                } header: {
                    Text("Local Data")
                } footer: {
                    Text("Favorites, recents, checklists, notes, review marks, and content edits are stored only on this device.")
                }

                Section {
                    if hideGovernanceCopy {
                        Label("Governance copy is hidden", systemImage: "eye.slash")
                    } else {
                        Button {
                            // Order matters, and so does the delay. The
                            // disclaimer is a fullScreenCover on RootTabView;
                            // asking the parent to present it in the same frame
                            // this sheet starts dismissing drops the
                            // presentation, so the sheet closed, nothing
                            // appeared, and the flag was left false — which
                            // ambushed the reader with the disclaimer at the
                            // next cold launch instead of showing it now.
                            dismiss()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) {
                                UserDefaults.standard.set(false, forKey: SettingsStorageKey.disclaimerAccepted)
                            }
                        } label: {
                            Label("Show Disclaimer Again", systemImage: "exclamationmark.shield")
                        }
                    }
                } header: {
                    Text("About")
                } footer: {
                    if !hideGovernanceCopy {
                        Text(AppConstants.clinicalDisclaimer)
                    }
                }

                Section("App") {
                    LabeledContent("Version", value: AppConstants.appVersionDescription)
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
            .navigationDestination(for: Kit.self) { kit in
                KitDetailView(kit: kit)
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
        case .clearKitChecklists: userData.clearAllKitChecklists()
        case .clearNotes: userData.clearAllNotes()
        case .clearReviews: userData.clearAllLocalReviews()
        case .clearEdits:
            editStore.resetEverything()
            repository.reapplyEdits()
        }
        confirmation = nil
    }
}

private enum DataAction: Identifiable {
    case clearRecents
    case clearFavorites
    case clearChecklists
    case clearKitChecklists
    case clearNotes
    case clearReviews
    case clearEdits

    var id: String { title }

    var title: String {
        switch self {
        case .clearRecents: return "Clear all recently viewed procedures?"
        case .clearFavorites: return "Remove all saved procedures?"
        case .clearChecklists: return "Reset every equipment checklist?"
        case .clearKitChecklists: return "Reset every kit room-setup checklist?"
        case .clearNotes: return "Delete all local notes?"
        case .clearReviews: return "Clear every local review mark?"
        case .clearEdits: return "Discard every local content edit and restore the bundled text?"
        }
    }

    var confirmLabel: String {
        switch self {
        case .clearRecents: return "Clear Recents"
        case .clearFavorites: return "Clear Saved"
        case .clearChecklists: return "Reset Checklists"
        case .clearKitChecklists: return "Reset Kit Checklists"
        case .clearNotes: return "Delete Notes"
        case .clearReviews: return "Clear Reviews"
        case .clearEdits: return "Discard Edits"
        }
    }
}
